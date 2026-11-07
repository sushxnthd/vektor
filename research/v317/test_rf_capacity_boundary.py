"""Independent grid and conservation checks for V317 conditional RF envelope."""
import math
import random
import unittest
from itertools import product

from research.v317.rf_capacity_boundary import Envelope, Range, FROZEN, rates, bound


class RFEnvelopeTests(unittest.TestCase):
    def test_synthetic_regimes(self):
        self.assertEqual(bound(FROZEN["bank_limited_predicted_win"])["decision"],
                         "conditionally_above_gate_not_validated")
        self.assertEqual(bound(FROZEN["cache_saturated_predicted_no_win"])["decision"],
                         "reject_under_assumptions")
        self.assertGreater(bound(FROZEN["mid_reuse_sensitivity"])["gain_upper"], 1.02)

    def test_zero_avoidance_with_nonnegative_overheads_never_wins(self):
        e = Envelope(2, 1, 4, 4, Range(0, 1), Range(0, 1), Range(0, 0),
                     Range(0, .5), Range(0, .5), Range(0, .5))
        self.assertLessEqual(bound(e)["gain_upper"], 1)

    def test_zero_demand_has_finite_rate(self):
        e = Envelope(2, 1, 4, 4, Range(1, 1), Range(0, 0), Range(0, 1),
                     Range(0, 0), Range(0, 0), Range(0, 0))
        self.assertEqual(bound(e)["gain_upper"], 1)

    def test_random_interior_contained_by_corner_certificate(self):
        rng = random.Random(20261031)
        for _ in range(300):
            hit = Range(*sorted((rng.random(), rng.random())))
            avoided = Range(*sorted((rng.random(), rng.random())))
            extra = Range(*sorted((rng.random(), rng.random())))
            ao = Range(0, rng.random() / 2)
            io = Range(0, rng.random() / 2)
            t = Range(0, rng.random() / 2)
            e = Envelope(rng.uniform(.5, 4), rng.uniform(.5, 4),
                         rng.uniform(.5, 8), rng.uniform(.5, 8), hit, extra,
                         avoided, ao, io, t)
            result = bound(e)
            for _ in range(100):
                x = [rng.uniform(z.lo, z.hi) for z in (hit, extra, avoided, ao, io, t)]
                gain = rates(e, *x)["ratio"]
                self.assertLessEqual(gain, result["gain_upper"] + 1e-10)
                self.assertGreaterEqual(gain, result["gain_lower"] - 1e-10)

    def test_exact_vertex_oracle_on_independent_enumeration(self):
        for e in FROZEN.values():
            result = bound(e)
            z = (e.hit, e.extra_reads, e.avoided_fraction, e.alu_overhead,
                 e.issue_overhead, e.period_penalty)
            independent = []
            for v in product(*((a.lo, a.hi) for a in z)):
                h, extra, f, ao, io, t = v
                d = e.logical_reads * (1 - h) + extra
                base = min(e.issue_width, e.alu_capacity,
                           e.read_ports / d if d else math.inf)
                dc = d * (1 - f)
                new = min(e.issue_width / (1 + io), e.alu_capacity / (1 + ao),
                          e.read_ports / dc if dc else math.inf) / (1 + t)
                independent.append(new / base)
            self.assertAlmostEqual(result["gain_lower"], min(independent))
            self.assertAlmostEqual(result["gain_upper"], max(independent))


if __name__ == "__main__":
    unittest.main()
