"""Independent exact-rational audit for the V317 bank-skew falsification.

Oracle below deliberately reimplements the throughput ratio without calling
bank_rate or candidate_gain. All cases are synthetic resource envelopes.
"""
from fractions import Fraction as F
import random
import unittest

from research.v317 import bank_skew_identifiability as model


def independent_oracle(ports, reads, removed, issue, alu,
                       issue_overhead=F(0), alu_overhead=F(0),
                       period_penalty=F(0)):
    def limit(ds, wi, ai):
        ans = min(wi, ai)
        for b in range(len(ports)):
            if ds[b] != 0:
                ans = min(ans, ports[b] / ds[b])
        return ans
    old = limit(reads, issue, alu)
    updated = tuple(reads[i] - removed[i] for i in range(len(ports)))
    new = limit(updated, issue / (1 + issue_overhead),
                alu / (1 + alu_overhead)) / (1 + period_penalty)
    return new / old


class BankSkewAudit(unittest.TestCase):
    def test_frozen_identical_aggregates_opposite_outcomes(self):
        self.assertEqual(sum(model.NO_WIN), sum(model.WIN))
        self.assertEqual(model.aggregate_gain(
            model.PORTS, model.NO_WIN, model.REMOVED,
            model.ISSUE, model.ALU), 1)
        self.assertEqual(model.aggregate_gain(
            model.PORTS, model.WIN, model.REMOVED,
            model.ISSUE, model.ALU), 1)
        self.assertEqual(model.candidate_gain(
            model.PORTS, model.NO_WIN, model.REMOVED,
            model.ISSUE, model.ALU), 1)
        self.assertEqual(model.candidate_gain(
            model.PORTS, model.WIN, model.REMOVED,
            model.ISSUE, model.ALU), F(5, 4))

    def test_exact_six_world_sweep(self):
        worlds = model.exhaustive_half_unit_worlds()
        self.assertEqual(len(worlds), 6)
        self.assertEqual(
            [F(w["banked_gain_exact"]) for w in worlds],
            [F(1), F(1), F(1), F(5, 4), F(5, 4), F(6, 5)])
        self.assertEqual(set(w["aggregate_gain_exact"] for w in worlds), {"1"})
        self.assertEqual(min(F(w["banked_gain_exact"]) for w in worlds), 1)
        self.assertEqual(max(F(w["banked_gain_exact"]) for w in worlds), F(5, 4))

    def test_independent_exact_oracle(self):
        for i in range(1, 7):
            reads = (F(i, 2), F(6 - i, 2))
            self.assertEqual(
                independent_oracle(model.PORTS, reads, model.REMOVED,
                                   model.ISSUE, model.ALU),
                model.candidate_gain(model.PORTS, reads, model.REMOVED,
                                     model.ISSUE, model.ALU))

    def test_per_bank_no_win_sufficiency(self):
        self.assertTrue(model.sufficient_no_win(
            model.PORTS, model.NO_WIN, model.ISSUE, model.ALU))
        self.assertFalse(model.sufficient_no_win(
            model.PORTS, model.WIN, model.ISSUE, model.ALU))
        for i in range(1, 7):
            reads = (F(i, 2), F(6 - i, 2))
            if model.sufficient_no_win(model.PORTS, reads,
                                       model.ISSUE, model.ALU):
                self.assertLessEqual(model.candidate_gain(
                    model.PORTS, reads, model.REMOVED,
                    model.ISSUE, model.ALU), 1)

    def test_overheads_cannot_improve_gain(self):
        for reads in (model.NO_WIN, model.WIN):
            ideal = model.candidate_gain(model.PORTS, reads, model.REMOVED,
                                         model.ISSUE, model.ALU)
            costly = model.candidate_gain(model.PORTS, reads, model.REMOVED,
                model.ISSUE, model.ALU, F(1, 10), F(1, 10), F(1, 20))
            self.assertLessEqual(costly, ideal)

    def test_random_independent_resource_oracle(self):
        rng = random.Random(31720261031)
        for _ in range(1000):
            ports = tuple(F(rng.randint(1, 8), 2) for _ in range(3))
            reads = tuple(F(rng.randint(0, 12), 4) for _ in range(3))
            removed = tuple(F(rng.randint(0, int(4 * d)), 4) for d in reads)
            issue = F(rng.randint(1, 12), 4)
            alu = F(rng.randint(1, 12), 4)
            overheads = tuple(F(rng.randint(0, 4), 20) for _ in range(3))
            self.assertEqual(
                independent_oracle(ports, reads, removed, issue, alu, *overheads),
                model.candidate_gain(ports, reads, removed, issue, alu,
                                     *overheads))

    def test_input_safety(self):
        with self.assertRaises(ValueError):
            model.candidate_gain(model.PORTS, model.NO_WIN, (F(2), F(0)),
                                 model.ISSUE, model.ALU)
        with self.assertRaises(ValueError):
            model.candidate_gain(model.PORTS, model.NO_WIN, model.REMOVED,
                                 model.ISSUE, model.ALU, F(-1, 10))
        with self.assertRaises(ValueError):
            model.bank_rate(model.PORTS, (F(1),), model.ISSUE, model.ALU)

    def test_report_does_not_claim_hardware_measurements(self):
        r = model.report()
        self.assertFalse(r["physical_gpu_measurements"])
        self.assertEqual(r["exact_gain_min"], "1")
        self.assertEqual(r["exact_gain_max"], "5/4")


if __name__ == "__main__":
    unittest.main()
