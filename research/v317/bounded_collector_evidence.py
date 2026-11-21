"""Machine-readable V317 bounded-collector synthetic evidence (stdout JSON)."""
import json
from research.v317.bounded_collector_exact import solve, independent_validate
from research.v317.test_two_class_collector_law import two_class_law

REGIMES = {
    "frozen_win": ((2,2,0),2),
    "frozen_no_win": ((2,2,2),4),
    "frozen_transfer": ((2,1,0),2),
    "falsified_K1": ((2,2,0),1),
    "unopened_transfer_321": ((3,2,1),2),
    "unopened_transfer_132": ((1,3,2),3),
    "unopened_transfer_303": ((3,0,3),2),
}
SENSITIVITY = ((2,2,0),(2,2,2),(2,1,0),
               (3,2,1),(1,3,2),(3,0,3))


def measured(counts, k):
    result = []
    for cand in (False,True):
        cycles, trace = solve(counts,k,cand)
        independent_validate(counts,k,cand,trace)
        result.append(cycles)
    return result


def main():
    rows = {}
    for name,(counts,k) in REGIMES.items():
        baseline,candidate = measured(counts,k)
        rows[name] = {
            "counts":list(counts),"collector_entries":k,
            "baseline_cycles":baseline,"candidate_cycles":candidate,
            "gain":baseline/candidate,
        }
    sensitivity = []
    for counts in SENSITIVITY:
        for k in range(1,7):
            baseline,candidate = measured(counts,k)
            sensitivity.append({
                "counts":list(counts),"collector_entries":k,
                "baseline_cycles":baseline,"candidate_cycles":candidate,
                "gain":baseline/candidate,
            })
    law_checks = 0
    for a in range(5):
        for b in range(5):
            if not a+b: continue
            for k in (1,2,3):
                if tuple(measured((a,b,0),k)) != two_class_law(a,b,k):
                    raise AssertionError("frozen two-class law falsified")
                law_checks += 1
    print(json.dumps({
        "evidence_tier":"exact finite synthetic bank-service cycles; NOT GPU IPC",
        "candidate":"hypothetical AB B-read elimination, not implemented",
        "equal_resource_model":"three 1-port banks, K collector entries each, completion width 2",
        "frozen_regimes":rows,
        "sensitivity":sensitivity,
        "two_class_law_worlds_checked":law_checks,
        "falsification":"frozen K=1 prediction 8/6 was wrong; actual 4/4",
    },sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
