#!/usr/bin/env python3
"""Development-only V317 queue/bank-port attribution, independent replay.

No holdout seeds. These are synthetic tile-level counts, not GPU IPC,
electrical bandwidth, or an SRAM/RTL measurement.
"""
import importlib.util
import json
from collections import deque, Counter
from pathlib import Path

p = Path(__file__).with_name("rotating_scan_prospective_20261120.py")
spec = importlib.util.spec_from_file_location("v317_sim", p)
sim = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sim)

def instrument(arrivals, rotating):
    q = deque()
    phase = 0
    stats = Counter()
    bank_use = [0] * sim.BANKS
    postwarm_completed = 0
    postwarm_bank_use = [0] * sim.BANKS
    postwarm_nonempty = 0
    postwarm_blocked = 0
    for t, batch in enumerate(arrivals):
        before = list(q)
        chosen = sim.grants(before, phase, rotating)
        phase ^= 1
        ports = [0] * sim.BANKS
        for i in chosen:
            a, b = before[i][1]
            ports[a] += 1
            ports[b] += 1
        assert max(ports) <= sim.PORTS
        for j, n in enumerate(ports):
            bank_use[j] += n
        if before:
            stats["nonempty_cycles"] += 1
            if len(chosen) < len(before):
                stats["blocked_cycles"] += 1
                stats["blocked_head_count"] += int(0 not in chosen)
            if len(chosen) == 0:
                stats["no_grant_nonempty"] += 1
            if len(chosen) == 1:
                stats["one_grant_nonempty"] += 1
        if t >= sim.WARMUP:
            postwarm_completed += len(chosen)
            postwarm_nonempty += int(bool(before))
            postwarm_blocked += int(bool(before) and len(chosen) < len(before))
            for j, n in enumerate(ports):
                postwarm_bank_use[j] += n
        for i in sorted(chosen, reverse=True):
            del q[i]
        for operands in batch:
            stats["offered"] += 1
            if len(q) < sim.CAP:
                q.append((t, operands))
                stats["admitted"] += 1
            else:
                stats["dropped"] += 1
        stats["queue_sum"] += len(q)
        stats["full_cycles"] += int(len(q) == sim.CAP)
        stats["cycles"] += 1
    stats["remaining"] = len(q)
    assert stats["offered"] == stats["admitted"] + stats["dropped"]
    assert stats["admitted"] == stats["offered"] - stats["dropped"]
    assert sum(bank_use) == 2 * (stats["admitted"] - stats["remaining"])
    assert sum(postwarm_bank_use) == 2 * postwarm_completed
    return dict(stats), bank_use, postwarm_completed, postwarm_bank_use, postwarm_nonempty, postwarm_blocked

def main():
    results = []
    # A single fixed development seed, all frozen workload classes/rates.
    for regime in sim.WEIGHTS:
        for rate in (1., 1.5, 2., 2.5, "burst"):
            arrivals = list(sim.trace(20261121, regime, rate, rate == "burst"))
            row = {"regime": regime, "rate": rate}
            for name, rotating in (("compact", False), ("rotating", True)):
                stats, banks, warm, warm_banks, warm_nonempty, warm_blocked = instrument(arrivals, rotating)
                original = sim.run(arrivals, rotating)
                assert warm == round(original["throughput"] * (sim.CYCLES - sim.WARMUP))
                for key in ("offered", "admitted", "dropped", "remaining"):
                    assert stats[key] == original[key], (regime, rate, name, key)
                row[name] = {
                    "throughput": original["throughput"],
                    "offered": stats["offered"],
                    "dropped": stats["dropped"],
                    "drop_fraction": stats["dropped"] / max(1, stats["offered"]),
                    "mean_queue": stats["queue_sum"] / stats["cycles"],
                    "full_cycle_fraction": stats["full_cycles"] / stats["cycles"],
                    "blocked_cycle_fraction": stats["blocked_cycles"] / stats["cycles"],
                    "one_grant_fraction": stats["one_grant_nonempty"] / max(1, stats["nonempty_cycles"]),
                    "bank_port_utilization": [x / (sim.CYCLES * sim.PORTS) for x in banks],
                    "postwarm_bank_port_utilization": [x / ((sim.CYCLES - sim.WARMUP) * sim.PORTS) for x in warm_banks],
                    "postwarm_blocked_nonempty_fraction": warm_blocked / max(1, warm_nonempty),
                    "postwarm_completed": warm,
                    "postwarm_port_work_conservation": sum(warm_banks) == 2 * warm,
                }
            row["ratio"] = row["rotating"]["throughput"] / row["compact"]["throughput"]
            results.append(row)
    print(json.dumps({"scope": "synthetic development seed 20261121; no holdouts",
                      "caveats": "bank-port utilization is a simulator proxy, not measured electrical traffic; all-cycle and postwarm counters are separated; per-bank port counts assume two operand accesses per completed synthetic request",
                      "results": results}, indent=2))

if __name__ == "__main__":
    main()
