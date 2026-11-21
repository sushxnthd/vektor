#!/usr/bin/env python3
"""V317/V296: falsifiable workload-level ceiling from bank-service oracle.

This is an OPTIMISTIC bound, not measured IPC. Assumptions: fraction f of
baseline cycles is serial bank-service time; oracle service ratio R>=1
reduces only that fraction; candidate clock period scales by c>=1.
No occupancy, queueing, or memory bandwidth improvements are assumed.
Any additional overhead makes the real result worse.
"""
from fractions import Fraction as F
import json
import unittest

def ceiling(service_ratio, bank_stall_fraction, clock_inflation):
    r, f, c = map(F, (service_ratio, bank_stall_fraction, clock_inflation))
    if r < 1 or not 0 <= f <= 1 or c <= 0:
        raise ValueError("invalid service ratio, fraction, or clock")
    # Amdahl serial decomposition, expressed in wall-clock time.
    return 1 / (c * ((1 - f) + f / r))

def break_even_clock(service_ratio, bank_stall_fraction):
    return ceiling(service_ratio, bank_stall_fraction, 1)

# PREDECLARED challenge regimes for future independent physical/workload runs.
# Oracle service ratios are PRIOR synthetic observations, not measured hardware.
REGIMES = {
    "predicted_no_win_uniform16": {
        "oracle_ratio": "1.001025", "rf_serial_fraction": "1/5",
        "clock_inflation": "101/100", "source": "frozen 4-slot uniform-16 oracle",
    },
    "predicted_possible_win_hotbank": {
        "oracle_ratio": "1.099869", "rf_serial_fraction": "4/5",
        "clock_inflation": "101/100", "source": "frozen 65%-hot-bank oracle",
    },
}

class Tests(unittest.TestCase):
    def test_no_bank_stalls(self):
        self.assertEqual(ceiling("3", 0, "11/10"), F(10, 11))
    def test_all_bank_stalls(self):
        self.assertEqual(ceiling("3/2", 1, "11/10"), F(15, 11))
    def test_no_service_gain(self):
        self.assertEqual(ceiling(1, "4/5", "11/10"), F(10, 11))
    def test_monotonicity(self):
        for f in (F(0), F(1, 5), F(4, 5), F(1)):
            self.assertLessEqual(ceiling("11/10", f, 1), ceiling("6/5", f, 1))
            self.assertGreaterEqual(ceiling("11/10", f, 1), ceiling("11/10", f, "101/100"))
    def test_frozen_signs(self):
        a = REGIMES["predicted_no_win_uniform16"]
        b = REGIMES["predicted_possible_win_hotbank"]
        self.assertLess(ceiling(a["oracle_ratio"], a["rf_serial_fraction"], a["clock_inflation"]), 1)
        self.assertGreater(ceiling(b["oracle_ratio"], b["rf_serial_fraction"], b["clock_inflation"]), 1)

if __name__ == "__main__":
    unittest.main(exit=False)
    print(json.dumps({
        k: {
            **v,
            "optimistic_speedup_ceiling": float(ceiling(v["oracle_ratio"], v["rf_serial_fraction"], v["clock_inflation"])),
            "break_even_clock_inflation": float(break_even_clock(v["oracle_ratio"], v["rf_serial_fraction"])),
            "evidence": "analytical ceiling only; not workload or routed timing",
        } for k, v in REGIMES.items()
    }, indent=2, sort_keys=True))
