"""Independent V303 value-carrying FP32 operand-cache update-port model.

Run: python -m research.v303.port_budget
Synthetic cycles and RF reads only. No silicon timing, power or GPU IPC.
"""
from __future__ import annotations

import hashlib
import json
from collections import OrderedDict
from dataclasses import asdict, dataclass
from typing import Iterable

from sim.vektor.pipeline import (
    Instruction, Wave, dependency_fma_kernel, reuse_fma_kernel,
)


@dataclass(frozen=True)
class Config:
    capacity: int = 64
    update_ports: int = 1
    policy: str = "limited_update"
    issue_width: int = 4
    rf_banks: int = 16
    rf_ports_per_bank: int = 2


@dataclass(frozen=True)
class Result:
    cycles: int
    issued: int
    rf_reads: int
    cache_hits: int
    cache_misses: int
    bank_stalls: int
    dependency_stalls: int
    resident_write_demand: int
    updates: int
    forced_invalidations: int
    max_cycle_demand: int
    max_cycle_updates: int
    stale_reads: int


def _digest(waves: Iterable[Wave]) -> str:
    serial = [
        [w.wave_id, [[i.op, list(i.src), i.dst, i.latency] for i in w.instructions]]
        for w in waves
    ]
    return hashlib.sha256(json.dumps(serial, separators=(",", ":")).encode()).hexdigest()


def simulate(input_waves: list[Wave], cfg: Config) -> Result:
    if cfg.policy not in ("invalidate", "limited_update", "ideal_update"):
        raise ValueError("invalid policy")
    if cfg.capacity < 0 or cfg.update_ports < 0 or cfg.issue_width < 1:
        raise ValueError("invalid resource configuration")
    if cfg.rf_banks < 1 or cfg.rf_ports_per_bank < 1:
        raise ValueError("invalid RF configuration")
    waves = [Wave(list(w.instructions), w.wave_id, w.pc, dict(w.ready_at)) for w in input_waves]
    if len({w.wave_id for w in waves}) != len(waves):
        raise ValueError("wave IDs must be unique")
    cache: OrderedDict[tuple[int, int], int] = OrderedDict()
    versions: dict[tuple[int, int], int] = {}
    cycle = 0
    round_robin = 0
    issued = rf_reads = hits = misses = bank_stalls = dependency_stalls = 0
    demand = updates = forced_invalidations = stale = max_demand = max_updates = 0

    def touch(key: tuple[int, int], value: int) -> None:
        if cfg.capacity == 0:
            return
        cache[key] = value
        cache.move_to_end(key)
        if len(cache) > cfg.capacity:
            cache.popitem(last=False)

    while any(not w.done for w in waves):
        cycle += 1
        if cycle > 1_000_000:
            raise RuntimeError("simulation exceeded one million cycles")
        cycle_issued = cycle_demand = cycle_updates = 0
        bank_reads: dict[int, int] = {}
        next_rr = round_robin
        for offset in range(len(waves)):
            if cycle_issued >= cfg.issue_width:
                break
            index = (round_robin + offset) % len(waves)
            wave = waves[index]
            if wave.done:
                continue
            ins = wave.instructions[wave.pc]
            if ins.op != "fp32":
                raise ValueError("FP32-only independent model; no load completion claim")
            if any(wave.ready_at.get(reg, 0) > cycle for reg in ins.src):
                dependency_stalls += 1
                continue
            needed: dict[int, int] = {}
            for reg in ins.src:
                key = (wave.wave_id, reg)
                if key not in cache:
                    bank = reg % cfg.rf_banks
                    needed[bank] = needed.get(bank, 0) + 1
            if any(bank_reads.get(bank, 0) + count > cfg.rf_ports_per_bank
                   for bank, count in needed.items()):
                bank_stalls += 1
                continue
            for reg in ins.src:
                key = (wave.wave_id, reg)
                true_version = versions.get(key, 0)
                if key in cache:
                    hits += 1
                    if cache[key] != true_version:
                        stale += 1
                        raise AssertionError(f"stale cache value at {key}")
                else:
                    misses += 1
                    rf_reads += 1
                    bank = reg % cfg.rf_banks
                    bank_reads[bank] = bank_reads.get(bank, 0) + 1
                touch(key, true_version)
            if ins.dst is not None:
                key = (wave.wave_id, ins.dst)
                new_version = versions.get(key, 0) + 1
                versions[key] = new_version
                if key in cache:
                    demand += 1
                    cycle_demand += 1
                    if cfg.policy == "ideal_update" or (
                        cfg.policy == "limited_update" and cycle_updates < cfg.update_ports
                    ):
                        updates += 1
                        cycle_updates += 1
                        # Updating a resident value does not change read-LRU order.
                        cache[key] = new_version
                    else:
                        forced_invalidations += 1
                        del cache[key]
                wave.ready_at[ins.dst] = cycle + ins.latency
            wave.pc += 1
            issued += 1
            cycle_issued += 1
            next_rr = (index + 1) % len(waves)
        max_demand = max(max_demand, cycle_demand)
        max_updates = max(max_updates, cycle_updates)
        round_robin = next_rr
    assert issued == sum(len(w.instructions) - w.pc for w in input_waves)
    assert demand == updates + forced_invalidations
    assert stale == 0
    return Result(cycle, issued, rf_reads, hits, misses, bank_stalls,
                  dependency_stalls, demand, updates, forced_invalidations,
                  max_demand, max_updates, stale)


def write_heavy_kernel(wave_count: int = 32, instructions: int = 64) -> list[Wave]:
    return [Wave([Instruction("fp32", (2, 0), dst=2, latency=1)
                  for _ in range(instructions)], w) for w in range(wave_count)]


def run() -> dict:
    workloads = {
        "H1_read_mostly": reuse_fma_kernel(),
        "H2_dependent_overwrite": dependency_fma_kernel(),
        "H3_write_heavy": write_heavy_kernel(),
    }
    rows = []
    for name, waves in workloads.items():
        for capacity in (0, 8, 64):
            results = {}
            for policy, ports in (("invalidate", 0), ("limited_update", 1),
                                  ("limited_update", 4), ("ideal_update", 0)):
                key = f"{policy}_p{ports}"
                results[key] = asdict(simulate(waves, Config(capacity, ports, policy)))
            base = results["invalidate_p0"]
            one = results["limited_update_p1"]
            four = results["limited_update_p4"]
            ideal = results["ideal_update_p0"]
            assert one["updates"] <= one["resident_write_demand"]
            assert four["updates"] <= four["resident_write_demand"]
            assert all(x["stale_reads"] == 0 for x in results.values())
            assert base["issued"] == one["issued"] == four["issued"] == ideal["issued"]
            if capacity == 0:
                assert base == one == four == ideal
            rows.append({
                "regime": name, "capacity": capacity, "trace_sha256": _digest(waves),
                "policies": results,
                "one_port_rf_read_reduction_pct": 100 * (base["rf_reads"] - one["rf_reads"]) / max(1, base["rf_reads"]),
                "one_port_cycle_change_pct": 100 * (one["cycles"] - base["cycles"]) / max(1, base["cycles"]),
            })
    h1 = next(x for x in rows if x["regime"] == "H1_read_mostly" and x["capacity"] == 64)
    h2 = next(x for x in rows if x["regime"] == "H2_dependent_overwrite" and x["capacity"] == 64)
    h3 = next(x for x in rows if x["regime"] == "H3_write_heavy" and x["capacity"] == 64)
    survives = (
        h2["one_port_rf_read_reduction_pct"] >= 5.0
        and h2["one_port_cycle_change_pct"] <= 1.0
        and h1["one_port_cycle_change_pct"] <= 1.0
        and h3["one_port_cycle_change_pct"] <= 1.0
    )
    return {"experiment": "v303_finite_port_coherent_operand_cache",
            "protocol": "research/v303/PORT_BUDGET_PROTOCOL.md",
            "scope": "FP32-only value-version simulation; no routed timing, power, GPU IPC",
            "survival_gate_passed": survives, "rows": rows}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
