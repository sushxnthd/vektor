#!/usr/bin/env python3
"""Fail-closed V296 matched routed feasibility audit from original job logs.

Source: GitHub Actions run 40646515864, frozen source SHA
84245c21f485c191aea7d352652c0ef036d6d047.
No inference is made about timed-out serial D8.
"""
from decimal import Decimal
from itertools import product
import json

RUN_ID = 40646515864
SETUP_GUARD_NS = Decimal("0.050")
HOLD_GUARD_NS = Decimal("0")
AREA_CEILING = Decimal("30000")
DATA = {
    4: {
        "pairwise": {"complete": True, "exit": 0, "area": "19543.01964701699", "setup": "0.066661", "hold": "0.010758", "cap_viol": 0, "slew_viol": 0},
        "serial_onehot": {"complete": True, "exit": 0, "area": "21914.94274939032", "setup": "-0.323617", "hold": "-0.011207", "cap_viol": 0, "slew_viol": 0},
    },
    8: {
        "pairwise": {"complete": True, "exit": 0, "area": "26723.956381147218", "setup": "0.059643", "hold": "0.011642", "cap_viol": 0, "slew_viol": 0},
        "serial_onehot": {"complete": False, "exit": 124, "area": None, "setup": None, "hold": None, "cap_viol": None, "slew_viol": None},
    },
}

def audit(rows=DATA):
    output = {}
    for depth in (4, 8):
        d = {}
        for name in ("pairwise", "serial_onehot"):
            r = rows[depth][name]
            if not r["complete"] or r["exit"] != 0 or any(r[k] is None for k in ("area", "setup", "hold", "cap_viol", "slew_viol")):
                d[name] = {"status": "CENSORED_INCOMPLETE", "pass": False}
                continue
            area, setup, hold = map(Decimal, (r["area"], r["setup"], r["hold"]))
            passes = (area <= AREA_CEILING and setup >= SETUP_GUARD_NS and hold >= HOLD_GUARD_NS
                      and r["cap_viol"] == 0 and r["slew_viol"] == 0)
            d[name] = {"status": "PASS" if passes else "FAIL", "pass": passes,
                       "setup_guard_headroom_ps": str(((setup-SETUP_GUARD_NS)*1000).quantize(Decimal("0.001"))),
                       "hold_headroom_ps": str((hold*1000).quantize(Decimal("0.001"))),
                       "area_headroom_um2": str(AREA_CEILING-area),
                       "integer_slices": int(AREA_CEILING // area)}
        matched_complete = all(rows[depth][name]["complete"] and rows[depth][name]["exit"] == 0 for name in ("pairwise", "serial_onehot"))
        matched_feasible = matched_complete and all(d[name]["pass"] for name in ("pairwise", "serial_onehot"))
        output[depth] = {"contestants": d, "matched_complete": matched_complete,
                         "matched_feasible": matched_feasible, "architectural_win_demonstrated": False,
                         "decision": "BOTH_COMPLETE_BUT_CONTROL_INFEASIBLE" if matched_complete and not matched_feasible else
                                     "CENSORED_CONTROL_TIMEOUT" if not matched_complete else "MATCHED_PHYSICAL_ONLY_NO_WORKLOAD_PROOF"}
    return output

def self_test():
    a = audit()
    assert a[4]["decision"] == "BOTH_COMPLETE_BUT_CONTROL_INFEASIBLE"
    assert a[8]["decision"] == "CENSORED_CONTROL_TIMEOUT"
    assert a[4]["contestants"]["pairwise"]["setup_guard_headroom_ps"] == "16.661"
    assert a[8]["contestants"]["pairwise"]["setup_guard_headroom_ps"] == "9.643"
    assert a[4]["contestants"]["serial_onehot"]["hold_headroom_ps"] == "-11.207"
    assert all(a[d]["contestants"]["pairwise"]["integer_slices"] == 1 for d in (4, 8))
    assert not any(a[d]["architectural_win_demonstrated"] for d in (4, 8))
    for candidate_complete, serial_complete, candidate_exit, serial_exit in product((False, True), repeat=4):
        test = {depth: {name: dict(DATA[depth][name]) for name in DATA[depth]} for depth in DATA}
        test[8]["pairwise"]["complete"] = candidate_complete
        test[8]["serial_onehot"]["complete"] = serial_complete
        test[8]["pairwise"]["exit"] = 0 if candidate_exit else 124
        test[8]["serial_onehot"]["exit"] = 0 if serial_exit else 124
        b = audit(test)[8]
        if not all((candidate_complete, serial_complete, candidate_exit, serial_exit)):
            assert not b["matched_complete"] and not b["matched_feasible"]
    print("V296_MATCHED_CENSOR_GATE_SELFTEST_PASS")

if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv:
        self_test()
    print(json.dumps({"run_id": RUN_ID, "source_sha": "84245c21f485c191aea7d352652c0ef036d6d047",
                      "evidence_tier": "ORIGINAL_CONTESTANT_JOB_LOGS_NOT_INDEPENDENT_AGGREGATE",
                      "audit": audit()}, indent=2))
