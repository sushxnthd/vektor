"""V317 prospective adversarial uniform-wire capacitance envelope.

This is an algebraic, pre-placement stress test on matched mapped Nangate45
netlists. It does NOT estimate actual wire RC or demonstrate routed legality.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

from research.v317.rtl.audit_rf_max_cap import (
    audit_core, liberty_pins, parse_netlist, bits
)

SWEEP_FF = (0.0, 0.5, 1.0, 2.0, 4.0)
WIRE_CAP_PER_UM_FF = (0.1, 0.2)


def apply_uniform_wire(rows, extra_wire_ff):
    """Evaluate the *same* extra capacitance on every mapped output net."""
    if not math.isfinite(extra_wire_ff) or extra_wire_ff < 0:
        raise ValueError("wire capacitance must be finite and nonnegative")
    if not rows:
        raise ValueError("no characterized mapped output nets")
    margins = [r["max_cap_ff"] - r["load_ff"] for r in rows]
    if any(not math.isfinite(m) for m in margins):
        raise ValueError("non-finite characterized margin")
    offenders = [
        {"net": r["net"], "cell": r["cell"], "instance": r["instance"],
         "base_load_ff": round(r["load_ff"], 6),
         "wire_cap_ff": extra_wire_ff,
         "limit_ff": r["max_cap_ff"],
         "margin_after_wire_ff": round(r["max_cap_ff"] - r["load_ff"] - extra_wire_ff, 6)}
        for r in rows if r["load_ff"] + extra_wire_ff > r["max_cap_ff"] + 1e-9
    ]
    offenders.sort(key=lambda r: (r["margin_after_wire_ff"], r["net"]))
    return {"extra_wire_cap_per_net_ff": extra_wire_ff,
            "violations": len(offenders),
            "all_mapped_internal_max_cap_legal": len(offenders) == 0,
            "worst_violations": offenders[:10]}


def extract_characterized_rows(netlist, lib, drive="BUF_X1", external_ff=24):
    """Use independent audit as an oracle and retain every characterized net."""
    reference = audit_core(netlist, lib, drive, external_ff)
    _, aliases, sinks, drivers, instances = parse_netlist(netlist, lib)
    buf_in = lib[drive]["A"]["cap_ff"]
    if buf_in is None:
        raise ValueError("uncharacterized buffer input")
    for i in range(4):
        sinks[aliases.root(f"grant[{i}]")] += buf_in
    rows = []
    for net, output_drivers in drivers.items():
        if len(output_drivers) != 1:
            raise ValueError(f"multiple output drivers on {net}")
        cell, instance, pin, limit = output_drivers[0]
        rows.append({"net": net, "cell": cell, "instance": instance,
                     "pin": pin, "load_ff": sinks[net], "max_cap_ff": limit})
    if len(rows) != reference["mapped_output_nets"] or instances != reference["mapped_instances"]:
        raise AssertionError("independent parser coverage disagrees")
    if round(min(r["max_cap_ff"] - r["load_ff"] for r in rows), 6) != reference["worst_internal"][0]["margin_ff"]:
        raise AssertionError("minimum margin disagrees with existing independent audit")
    if not reference["output_buffer"]["legal"]:
        raise AssertionError("matched external buffer output is not legal at 24 fF")
    return rows, reference


def analyze(netlist, lib):
    rows, oracle = extract_characterized_rows(netlist, lib)
    threshold = min(r["max_cap_ff"] - r["load_ff"] for r in rows)
    if threshold < 0:
        raise AssertionError("already electrically illegal at zero wire")
    sweep = {str(c): apply_uniform_wire(rows, c) for c in SWEEP_FF}
    worst = sorted(rows, key=lambda r: (r["max_cap_ff"] - r["load_ff"], r["net"]))[:10]
    return {
        "mapped_instances": oracle["mapped_instances"],
        "characterized_output_nets": len(rows),
        "uncharacterized_primary_input_drivers": oracle["uncharacterized_primary_input_drivers"],
        "matched_output_stage": {"cell": "BUF_X1", "load_ff": 24,
                                 "external_max_cap_legal_at_zero_wire": True},
        "uniform_extra_wire_cap_limit_ff": round(threshold, 6),
        "hypothetical_max_uniform_wire_length_um": {
            str(cap): round(threshold / cap, 6) for cap in WIRE_CAP_PER_UM_FF
        },
        "worst_internal": [
            {"net": r["net"], "cell": r["cell"], "instance": r["instance"],
             "load_ff": round(r["load_ff"], 6), "max_cap_ff": r["max_cap_ff"],
             "remaining_wire_budget_ff": round(r["max_cap_ff"] - r["load_ff"], 6)}
            for r in worst
        ],
        "sweep": sweep,
    }


def verify_frozen(source, pairwise):
    def legal(design, c):
        return design["sweep"][str(float(c))]["all_mapped_internal_max_cap_legal"]
    predictions = {
        "zero_wire_both_legal": legal(source, 0) and legal(pairwise, 0),
        "half_ff_both_legal": legal(source, 0.5) and legal(pairwise, 0.5),
        "one_ff_source_fails_pairwise_survives": not legal(source, 1) and legal(pairwise, 1),
        "two_ff_source_fails_pairwise_survives": not legal(source, 2) and legal(pairwise, 2),
        "four_ff_both_fail": not legal(source, 4) and not legal(pairwise, 4),
        "thresholds_match_frozen_oracle": (
            abs(source["uniform_extra_wire_cap_limit_ff"] - 0.680998) < 1e-5
            and abs(pairwise["uniform_extra_wire_cap_limit_ff"] - 3.838028) < 1e-5
        ),
        "upstream_primary_input_remains_uncharacterized": (
            len(source["uncharacterized_primary_input_drivers"]) >= 1
            and len(pairwise["uncharacterized_primary_input_drivers"]) >= 1
        ),
    }
    return predictions


def main():
    p = argparse.ArgumentParser()
    p.add_argument("liberty", type=Path)
    p.add_argument("source_netlist", type=Path)
    p.add_argument("pairwise_netlist", type=Path)
    args = p.parse_args()
    lib = liberty_pins(args.liberty.read_text())
    source = analyze(args.source_netlist.read_text(), lib)
    pairwise = analyze(args.pairwise_netlist.read_text(), lib)
    frozen = verify_frozen(source, pairwise)
    result = {
        "evidence_tier": "MAPPED_CELL_PIN_PLUS_ADVERSARIAL_UNIFORM_WIRE_CAP; NOT PLACED_OR_ROUTED",
        "frozen_predictions": frozen,
        "all_frozen_predictions_pass": all(frozen.values()),
        "source": source,
        "pairwise": pairwise,
        "routed_wire_rc_extracted": False,
        "primary_input_driver_characterized": False,
        "gpu_throughput_measured": False,
        "intrinsic_grant_equivalent_service_gain": 1.0,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["all_frozen_predictions_pass"]:
        raise SystemExit("frozen wire-capacitance prediction failed")


if __name__ == "__main__":
    main()
