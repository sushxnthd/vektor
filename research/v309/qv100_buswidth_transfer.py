#!/usr/bin/env python3
"""Independent, fail-closed cross-workload QV100 bus-width sensitivity audit.

Two complete original workloads, no hardware counters or architecture speedup.
Predictions were frozen in QV100_LUD_BUSWIDTH_TRANSFER_PREREG_20261031.md.
"""
import argparse
import copy
import json
import math
from pathlib import Path

WIDTHS = (8, 32)
CYCLE_KEYS = ("gpu_tot_sim_cycle", "gpu_tot_sim_insn")
MEM_KEYS = ("L1D_total_cache_misses", "L2_total_cache_misses",
            "gpgpu_n_mem_read_global", "gpgpu_n_mem_write_global")
TIER = "pinned_accel_sim_QV100_SASS_only_not_hardware"


def natural(value, label, positive=False):
    if type(value) is not int or value < (1 if positive else 0):
        raise ValueError("invalid integer: " + label)
    return value


def validate_selection(first, second):
    if first.get("status") != "SELECTED_INPUT_ONLY":
        raise ValueError("first workload not prospectively selected")
    if second.get("status") != "SECOND_WORKLOAD_SELECTED_INPUT_ONLY":
        raise ValueError("second workload not prospectively selected")
    if second.get("selection_rank_one_based") != 2 or second.get("complete_candidate_count", 0) < 2:
        raise ValueError("rank-two source-selection provenance invalid")
    a, b = first.get("selected_list"), second.get("selected_list")
    if not isinstance(a, str) or not isinstance(b, str) or not a.endswith("/kernelslist.g") or not b.endswith("/kernelslist.g"):
        raise ValueError("invalid original trace identities")
    if a == b or second.get("first_workload_list") != a:
        raise ValueError("source-selected workloads not distinct and ordered")
    for d in (first, second):
        natural(d.get("kernel_launches"), "selection launches", True)
        if d.get("hardware_validated") is not False or d.get("architecture_speedup_permitted") is not False:
            raise ValueError("source manifest overclaims evidence")
    return a, b


def validate_audit(audit, selection):
    if (audit.get("status") != "PASS_INDEPENDENT_SIMULATOR_COUNTER_REPLAY"
            or audit.get("evidence_tier") != TIER
            or audit.get("semantic_kernel_counters_identical") is not True
            or audit.get("hardware_validated") is not False
            or audit.get("architecture_speedup_permitted") is not False
            or audit.get("selected_list") != selection["selected_list"]
            or audit.get("expected_launches") != selection["kernel_launches"]):
        raise ValueError("baseline not an independent simulator audit")
    totals = audit.get("cumulative_counter_totals")
    rows = audit.get("kernel_records")
    if not isinstance(totals, dict) or not isinstance(rows, list) or len(rows) != selection["kernel_launches"]:
        raise ValueError("invalid baseline per-kernel evidence")
    for key in CYCLE_KEYS + MEM_KEYS:
        value = natural(totals.get(key), key, key in CYCLE_KEYS)
        if rows[-1].get(key) != value or sum(r.get("increments", {}).get(key, -1) for r in rows) != value:
            raise ValueError("baseline counter conservation failed: " + key)
    hashes = audit.get("raw_log_sha256")
    if not isinstance(hashes, list) or len(hashes) != 2 or not all(isinstance(h, str) and len(h) == 64 for h in hashes):
        raise ValueError("baseline raw log provenance absent")
    return totals


def validate_sweep(sweep, audit, totals):
    if (sweep.get("status") != "PASS_INDEPENDENT_BUSWIDTH_AUDIT"
            or sweep.get("hardware_calibrated") is not False
            or sweep.get("equal_resource_architecture_comparison") is not False
            or sweep.get("physical_speedup_demonstrated") is not False):
        raise ValueError("bus-width sweep evidence tier invalid")
    if (sweep.get("baseline_sim_cycles") != totals["gpu_tot_sim_cycle"]
            or sweep.get("baseline_sim_instructions") != totals["gpu_tot_sim_insn"]
            or sweep.get("raw_log_sha256", {}).get("baseline") != audit["raw_log_sha256"]):
        raise ValueError("bus-width baseline does not match independent replay")
    for key in ("L1D_total_cache_misses", "L2_total_cache_misses"):
        if sweep.get("baseline_cache_counters", {}).get(key) != totals[key]:
            raise ValueError("baseline cache counters drift")
    rows = sweep.get("variants")
    if not isinstance(rows, list) or len(rows) != 2 or [r.get("buswidth_bytes") for r in rows] != list(WIDTHS):
        raise ValueError("variant width/order drift")
    cycles = totals["gpu_tot_sim_cycle"]
    for row in rows:
        width = row["buswidth_bytes"]
        c = natural(row.get("sim_cycles"), "variant cycles", True)
        if row.get("cycle_delta") != c - cycles:
            raise ValueError("variant delta drift")
        pct = row.get("cycle_delta_percent")
        if type(pct) not in (float, int) or not math.isfinite(pct) or not math.isclose(pct, 100.0*(c/cycles-1), rel_tol=1e-9, abs_tol=1e-8):
            raise ValueError("variant percentage drift")
        hashes = sweep.get("raw_log_sha256", {}).get(str(width))
        if not isinstance(hashes, list) or len(hashes) != 2 or not all(isinstance(h, str) and len(h) == 64 for h in hashes):
            raise ValueError("variant raw log provenance absent")
        for key in ("L1D_total_cache_misses", "L2_total_cache_misses"):
            natural(row.get("counters", {}).get(key), "variant " + key)
        if row.get("cache_counters_match_baseline") is not all(row["counters"][key] == totals[key] for key in ("L1D_total_cache_misses", "L2_total_cache_misses")):
            raise ValueError("variant cache-invariance claim drift")
    if sweep.get("counter_invariance") is not all(row["cache_counters_match_baseline"] for row in rows):
        raise ValueError("aggregate cache-invariance claim drift")
    predictions = {"p1_narrower_is_slower": rows[0]["sim_cycles"] > cycles,
                   "p2_wider_not_slower": rows[1]["sim_cycles"] <= cycles,
                   "p3_small_widening_benefit": (cycles-rows[1]["sim_cycles"])/cycles < 0.02}
    if sweep.get("predictions") != predictions:
        raise ValueError("upstream sweep prediction drift")
    return {"baseline_cycles": cycles, "narrow_cycles": rows[0]["sim_cycles"],
            "wide_cycles": rows[1]["sim_cycles"],
            "widening_gain_fraction": (cycles-rows[1]["sim_cycles"])/cycles,
            "narrowing_cycle_penalty_fraction": (rows[0]["sim_cycles"]-cycles)/cycles,
            "reported_global_reads_per_instruction": totals["gpgpu_n_mem_read_global"]/totals["gpu_tot_sim_insn"],
            "reported_global_writes_per_instruction": totals["gpgpu_n_mem_write_global"]/totals["gpu_tot_sim_insn"],
            "cache_counter_invariance": sweep["counter_invariance"]}


def compare(first_selection, second_selection, first_audit, second_audit, first_sweep, second_sweep):
    a, b = validate_selection(first_selection, second_selection)
    x = validate_sweep(first_sweep, first_audit, validate_audit(first_audit, first_selection))
    y = validate_sweep(second_sweep, second_audit, validate_audit(second_audit, second_selection))
    p1 = y["widening_gain_fraction"] < 0.02
    p2 = y["narrow_cycles"] >= y["baseline_cycles"]
    p3 = x["widening_gain_fraction"] < 0.02 and p1
    return {"status": "PASS_INDEPENDENT_TWO_WORKLOAD_SENSITIVITY_AUDIT",
            "first_original_workload": a, "second_original_workload": b,
            "first": x, "second": y,
            "frozen_predictions": {"P1_LUD_widening_below_2pct": p1,
                                   "P2_LUD_narrowing_not_faster": p2,
                                   "P3_both_widening_below_2pct": p3},
            "all_frozen_predictions_survived": p1 and p2 and p3,
            "interpretation": "parameter sensitivity only; no architectural speedup or DRAM-byte measurement",
            "hardware_calibrated": False, "physical_speedup_demonstrated": False,
            "RTX_5090_equivalence": False}


def selftest():
    def selection(name, rank):
        return {"status": "SELECTED_INPUT_ONLY" if rank == 1 else "SECOND_WORKLOAD_SELECTED_INPUT_ONLY",
                "selection_rank_one_based": rank, "complete_candidate_count": 11,
                "selected_list": name+"/kernelslist.g", "first_workload_list": "a/kernelslist.g",
                "kernel_launches": 1, "hardware_validated": False, "architecture_speedup_permitted": False}
    def audit(s, cycles):
        totals = dict(zip(CYCLE_KEYS+MEM_KEYS, (cycles, 100, 20, 5, 30, 10)))
        return {"status": "PASS_INDEPENDENT_SIMULATOR_COUNTER_REPLAY", "evidence_tier": TIER,
                "semantic_kernel_counters_identical": True, "hardware_validated": False,
                "architecture_speedup_permitted": False, "selected_list": s["selected_list"],
                "expected_launches": 1, "cumulative_counter_totals": totals,
                "kernel_records": [dict(totals, increments=dict(totals))],
                "raw_log_sha256": ["a"*64, "b"*64]}
    def sweep(a, narrow, wide):
        c = a["cumulative_counter_totals"]["gpu_tot_sim_cycle"]
        rows = [{"buswidth_bytes": w, "sim_cycles": n, "cycle_delta": n-c,
                 "cycle_delta_percent": 100*(n/c-1),
                 "counters": {"L1D_total_cache_misses": 20, "L2_total_cache_misses": 5},
                 "cache_counters_match_baseline": True} for w,n in ((8,narrow),(32,wide))]
        return {"status": "PASS_INDEPENDENT_BUSWIDTH_AUDIT",
                "hardware_calibrated": False, "equal_resource_architecture_comparison": False,
                "physical_speedup_demonstrated": False, "baseline_sim_cycles": c,
                "baseline_sim_instructions": 100,
                "baseline_cache_counters": {"L1D_total_cache_misses": 20, "L2_total_cache_misses": 5},
                "variants": rows, "counter_invariance": True,
                "raw_log_sha256": {"baseline": a["raw_log_sha256"], "8": ["c"*64,"d"*64], "32": ["e"*64,"f"*64]},
                "predictions": {"p1_narrower_is_slower": narrow>c,
                                "p2_wider_not_slower": wide<=c,
                                "p3_small_widening_benefit": (c-wide)/c<0.02}}
    s1,s2 = selection("a",1),selection("b",2)
    a1,a2 = audit(s1,1000),audit(s2,2000)
    w1,w2 = sweep(a1,1010,1000),sweep(a2,2020,1990)
    args=[s1,s2,a1,a2,w1,w2]
    assert compare(*args)["all_frozen_predictions_survived"]
    assert not compare(s1,s2,a1,a2,w1,sweep(a2,2020,1900))["all_frozen_predictions_survived"]
    mutations = [
        (0, lambda x: x.update(status="UNFROZEN")),
        (1, lambda x: x.update(first_workload_list="wrong/kernelslist.g")),
        (2, lambda x: x.update(hardware_validated=True)),
        (3, lambda x: x.update(expected_launches=2)),
        (3, lambda x: x["kernel_records"][0]["increments"].update(gpgpu_n_mem_write_global=11)),
        (4, lambda x: x.update(physical_speedup_demonstrated=True)),
        (5, lambda x: x["variants"][0].update(sim_cycles=1)),
        (5, lambda x: x["raw_log_sha256"].update(baseline=["z"*64])),
        (5, lambda x: x["variants"][1].update(buswidth_bytes=64)),
        (5, lambda x: x.update(counter_invariance=False)),
    ]
    for i, mutate in mutations:
        bad=copy.deepcopy(args)
        mutate(bad[i])
        try:
            compare(*bad)
        except (ValueError, TypeError, KeyError):
            continue
        raise AssertionError("forged cross-workload evidence accepted")
    return {"status":"PASS","positive_controls":2,"negative_controls":len(mutations)}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    for key in ("first-selection","second-selection","first-audit","second-audit","first-sweep","second-sweep","out"):
        p.add_argument("--"+key)
    a=p.parse_args()
    if a.selftest:
        result=selftest()
    else:
        fields=("first_selection","second_selection","first_audit","second_audit","first_sweep","second_sweep")
        if any(not getattr(a,k) for k in fields) or not a.out:
            p.error("provide six original evidence inputs and --out")
        result=compare(*(json.loads(Path(getattr(a,k)).read_text()) for k in fields))
        Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
