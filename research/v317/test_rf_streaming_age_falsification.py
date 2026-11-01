"""Independent regression checks for V317 synthetic RF queueing results."""
import unittest
from itertools import product
from research.v317.rf_streaming_age_falsification import (
    legal, priority, exact, two_bank_closed_form, two_bank_priority_drain,
    theorem_audit, arrivals, simulate,
)
from research.v317.rf_streaming_strong_controls import (
    oldest_greedy, RotatingPriority,
)
from research.v317.rf_arbiter_port_audit import (
    rtl_priority_model, optimal_grant,
)


class TestV317StreamingAge(unittest.TestCase):
    def test_bank_ports_charged_per_operand(self):
        self.assertTrue(legal(1, [(0, 0)] * 4))
        self.assertFalse(legal(3, [(0, 0)] * 4))
        self.assertTrue(legal(3, [(0, 1)] * 4))
        self.assertFalse(legal(7, [(0, 1)] * 4))

    def test_exhaustive_source_priority_and_exact_legal(self):
        for valid in range(16):
            for bits in product(range(2), repeat=8):
                pairs = [(bits[2*i], bits[2*i+1]) for i in range(4)]
                p = priority(valid, pairs)
                e = exact(valid, pairs)
                self.assertEqual(p & ~valid, 0)
                self.assertTrue(legal(p, pairs))
                self.assertTrue(legal(e, pairs))
                self.assertLessEqual(p.bit_count(), e.bit_count())
                self.assertEqual(p, rtl_priority_model(valid, pairs))
                self.assertEqual(e, optimal_grant(valid, pairs))

    def test_long_two_bank_closed_form(self):
        self.assertEqual(
            theorem_audit(), {"checked": 6400, "counterexample": None}
        )
        self.assertEqual(two_bank_closed_form(2, 3, 5), 6)
        pairs = [(0, 0)] * 2 + [(1, 1)] * 3 + [(0, 1)] * 5
        self.assertEqual(two_bank_priority_drain(pairs), 6)

    def test_frozen_no_win_and_failed_win(self):
        private = arrivals("private", 0.55, 317110)
        self.assertEqual(
            simulate(private, priority), simulate(private, exact)
        )
        hotspot = arrivals("four_bank", 0.48, 317111)
        p = simulate(hotspot, priority)
        e = simulate(hotspot, exact)
        self.assertLess(
            e["completed_after_warmup"] /
            p["completed_after_warmup"], 1.01
        )

    def test_simple_fairness_controls(self):
        stream = arrivals("four_bank", 0.60, 317260)
        rr = simulate(stream, RotatingPriority())
        greedy = simulate(stream, oldest_greedy)
        self.assertLess(rr["backlog_total"], 100)
        self.assertLess(greedy["backlog_total"], 100)
        self.assertLess(rr["latency_p99_cycles"], 100)


if __name__ == "__main__":
    unittest.main()
