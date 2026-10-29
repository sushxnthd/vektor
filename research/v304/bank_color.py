"""V304 frozen static RF-bank coloring test; synthetic, not GPU IPC."""
from __future__ import annotations
import json
import random
from collections import Counter
from dataclasses import asdict, dataclass

BANKS, ISSUE, INSTRUCTIONS = 16, 4, 128
SEEDS = tuple(range(901, 921))

def bank(policy: str, wave: int, reg: int) -> int:
    if policy == "modulo":
        return reg % BANKS
    if policy == "xor":
        return (reg ^ (2 * wave)) % BANKS
    if policy == "add":
        return (reg + 2 * wave) % BANKS
    raise ValueError(policy)

def trace(regime: str, seed: int):
    rng = random.Random(seed)
    n = 4 if regime == "H4_low_occupancy" else 32
    out = []
    for wave in range(n):
        instr = []
        for pc in range(INSTRUCTIONS):
            if regime in ("H1_aligned", "H3_two_ports", "H4_low_occupancy"):
                regs = (0, 1)
            elif regime == "H2_random":
                regs = (rng.randrange(32), rng.randrange(32))
            elif regime == "H5_phase_shift":
                x = ((pc // 8) + (wave // 4)) % 16
                regs = (x, (x + 1) % 32)
            else:
                raise ValueError(regime)
            instr.append(regs)
        out.append(instr)
    return out, 2 if regime == "H3_two_ports" else 1

@dataclass(frozen=True)
class Result:
    cycles: int
    instructions: int
    throughput: float
    bank_conflict_deferrals: int
    empty_cycles: int
    max_bank_demand: int

def run(traces, policy: str, ports: int) -> Result:
    """Four operand collectors; same-bank distinct reads serialize across cycles."""
    n = len(traces)
    pc = [0] * n
    remaining = [None] * n
    done, rr, cycles, conflicts, empty, max_demand = 0, 0, 0, 0, 0, 0
    while done < n * INSTRUCTIONS:
        cycles += 1
        if cycles > n * INSTRUCTIONS * 100:
            raise RuntimeError("deadlock")
        used = Counter()
        issued = selected = 0
        next_rr = rr
        for offset in range(n):
            if selected == ISSUE:
                break
            w = (rr + offset) % n
            if pc[w] >= len(traces[w]):
                continue
            selected += 1
            if remaining[w] is None:
                remaining[w] = set(traces[w][pc[w]])
            for reg in sorted(tuple(remaining[w])):
                b = bank(policy, w, reg)
                if used[b] >= ports:
                    conflicts += 1
                    continue
                used[b] += 1
                remaining[w].remove(reg)
            max_demand = max(max_demand, max(used.values(), default=0))
            if not remaining[w]:
                pc[w] += 1
                done += 1
                issued += 1
                remaining[w] = None
                next_rr = (w + 1) % n
        rr = next_rr
        if issued == 0:
            empty += 1
    assert pc == [len(t) for t in traces]
    return Result(cycles, done, done / cycles, conflicts, empty, max_demand)

def independent_check():
    mapping_checks = 0
    for policy in ("modulo", "xor", "add"):
        for w in range(32):
            assert sorted(bank(policy, w, r) for r in range(16)) == list(range(16))
            mapping_checks += 1
    oracle_checks = 0
    for policy in ("modulo", "xor", "add"):
        for w1 in range(8):
            for w2 in range(8):
                for r in range(16):
                    s1 = {bank(policy, w1, r), bank(policy, w1, (r+1)%16)}
                    s2 = {bank(policy, w2, r), bank(policy, w2, (r+1)%16)}
                    load = [int(b in s1) + int(b in s2) for b in range(16)]
                    assert (not (s1 & s2)) == (max(load) <= 1)
                    oracle_checks += 1
    return {"mapping_checks": mapping_checks, "pair_oracle_checks": oracle_checks}

def experiment():
    checks = independent_check()
    rows = []
    regimes = ("H1_aligned", "H2_random", "H3_two_ports", "H4_low_occupancy", "H5_phase_shift")
    for regime in regimes:
        for seed in SEEDS:
            t, ports = trace(regime, seed)
            controls = {p: asdict(run(t, p, ports)) for p in ("modulo", "xor", "add")}
            rows.append({"regime": regime, "seed": seed, "ports": ports, "policies": controls})
    summary = {}
    for regime in regimes:
        rs = [r for r in rows if r["regime"] == regime]
        summary[regime] = {
            p: {"mean_throughput": sum(r["policies"][p]["throughput"] for r in rs)/len(rs),
                "mean_cycles": sum(r["policies"][p]["cycles"] for r in rs)/len(rs),
                "mean_conflicts": sum(r["policies"][p]["bank_conflict_deferrals"] for r in rs)/len(rs)}
            for p in ("modulo", "xor", "add")
        }
        summary[regime]["add_vs_xor_pct"] = 100*(summary[regime]["add"]["mean_throughput"]/summary[regime]["xor"]["mean_throughput"]-1)
        summary[regime]["add_vs_modulo_pct"] = 100*(summary[regime]["add"]["mean_throughput"]/summary[regime]["modulo"]["mean_throughput"]-1)
    return {"name": "v304-static-bank-coloring", "evidence_tier": "synthetic",
            "checks": checks, "rows": rows, "summary": summary,
            "frozen_survival": {"h1_add_vs_xor_at_least_pct": 5, "h2_add_vs_xor_not_below_pct": -2},
            "survives": summary["H1_aligned"]["add_vs_xor_pct"] >= 5 and summary["H2_random"]["add_vs_xor_pct"] >= -2}

if __name__ == "__main__":
    print(json.dumps(experiment(), indent=2, sort_keys=True))
