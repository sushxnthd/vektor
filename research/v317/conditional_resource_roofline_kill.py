#!/usr/bin/env python3
"""Conservative conditional throughput ceiling; synthetic examples, not GPU evidence.

Each supplied fraction must independently upper-bound the fraction of cycles
eligible for candidate service. Their intersection is bounded by their MINIMUM,
not their product. In particular, do not use a control-overhead estimate unless
it proves a minimum fraction of globally service-blocked cycles. If that is
unknown, use overhead=0 (no reduction). The measured baseline must use the
same request unit, horizon and resource budget as the candidate.
"""
import argparse
import json
import math


def bound(baseline_measured, candidate_bank, issue, output, memory,
          occupancy, overhead):
    values = (baseline_measured, candidate_bank, issue, output, memory,
              occupancy, overhead)
    if any(type(v) not in (int, float) or not math.isfinite(v)
           for v in values):
        raise ValueError("finite numeric inputs required")
    if any(v <= 0 for v in values[:6]):
        raise ValueError("positive rates and occupancy required")
    if not 0 < occupancy <= 1 or not 0 <= overhead < 1:
        raise ValueError("invalid eligible-cycle bounds")
    service = min(candidate_bank, issue, output, memory)
    eligible_upper = min(occupancy, 1 - overhead)
    ceiling = service * eligible_upper
    return {"baseline_measured": baseline_measured,
            "candidate_ceiling": ceiling,
            "ceiling_over_baseline": ceiling / baseline_measured,
            "conditional_kill": ceiling <= baseline_measured,
            "eligible_cycle_upper": eligible_upper,
            "assumptions": "occupancy and (1-overhead) are independently established upper bounds on eligible service-cycle fraction; same throughput units and matched resources"}


def selftest():
    # Prospective illustrative regimes, NOT real measurements or holdouts.
    win = bound(.75, 2, 2, 2, 2, .75, .05)
    no = bound(.6, 2, 2, .7, 2, .75, .05)
    assert abs(win["ceiling_over_baseline"] - 2.0) < 1e-12
    assert not win["conditional_kill"]
    assert abs(no["ceiling_over_baseline"] - .875) < 1e-12
    assert no["conditional_kill"]
    # Overlapping inactive/control-blocked cycles: multiplicative .25 is invalid.
    overlap = bound(.5, 1, 1, 1, 1, .5, .5)
    assert overlap["candidate_ceiling"] == .5
    assert overlap["candidate_ceiling"] != .25
    # Unknown control-blocked-cycle lower bound: overhead=0.
    assert bound(.5, 1, 1, 1, 1, .5, 0)["candidate_ceiling"] == .5
    for params in [(1,2,2,2,2,0,0), (1,2,2,2,2,1,1),
                   (0,2,2,2,2,1,0), (1,2,2,2,2,1,float("nan")),
                   (1,2,2,2,2,1,True)]:
        try:
            bound(*params)
        except ValueError:
            pass
        else:
            raise AssertionError(params)
    print(json.dumps({"predicted_bank_limited": win,
                      "predicted_output_limited": no,
                      "evidence": "synthetic conditional ceiling only",
                      "warning": "Do not use a control-overhead reduction without a proven lower bound on globally blocked cycles. Positive ceiling gaps never establish speedups."}, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()
    if a.selftest:
        selftest()
    else:
        p.error("use --selftest; no real matched-resource baseline supplied")
