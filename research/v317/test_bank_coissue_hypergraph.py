"""Independent labeled-instruction maximum-matching oracle for V317.

Does not call the production DP to compute expected cycles. Every instruction
is a labeled vertex; compatible disjoint-mask pairs form matching edges.
"""
from functools import lru_cache
from itertools import product
import random
import unittest

from research.v317 import bank_coissue_hypergraph as model


def matching_oracle(masks):
    n = len(masks)

    @lru_cache(None)
    def maximum_pairs(remaining):
        if remaining == 0:
            return 0
        i = (remaining & -remaining).bit_length() - 1
        without_i = remaining ^ (1 << i)
        best = maximum_pairs(without_i)
        for j in range(i + 1, n):
            if without_i & (1 << j) and (masks[i] & masks[j]) == 0:
                best = max(best, 1 + maximum_pairs(without_i ^ (1 << j)))
        return best

    return n - maximum_pairs((1 << n) - 1)


def labeled_masks(counts, classes):
    return [mask for n, mask in zip(counts, classes) for _ in range(n)]


class IndependentAtomicBankAudit(unittest.TestCase):
    def test_frozen_prospective_cases(self):
        for counts, baseline, candidate in [
            ((2, 2, 2), 6, 4),
            ((0, 3, 3), 6, 6),
            ((2, 1, 3), 6, 5),
        ]:
            self.assertEqual(matching_oracle(labeled_masks(counts, model.BASE)), baseline)
            self.assertEqual(matching_oracle(labeled_masks(counts, model.CANDIDATE)), candidate)
            self.assertEqual(model.schedule_cycles(counts, model.BASE), baseline)
            self.assertEqual(model.schedule_cycles(counts, model.CANDIDATE), candidate)
            self.assertEqual(model.mean_capacity_lower_bound(counts, model.BASE),
                             model.mean_capacity_lower_bound(counts, model.CANDIDATE))

    def test_all_124_frozen_sensitivity_worlds(self):
        false_no_win = 0
        gains = []
        for counts in product(range(5), repeat=3):
            if not any(counts):
                continue
            b = matching_oracle(labeled_masks(counts, model.BASE))
            c = matching_oracle(labeled_masks(counts, model.CANDIDATE))
            self.assertEqual(b, model.schedule_cycles(counts, model.BASE))
            self.assertEqual(c, model.schedule_cycles(counts, model.CANDIDATE))
            self.assertEqual(b, sum(counts))
            self.assertEqual(c, sum(counts) - min(counts[0], counts[1]))
            for masks, cycles in [(model.BASE, b), (model.CANDIDATE, c)]:
                self.assertLessEqual(model.mean_capacity_lower_bound(counts, masks), cycles)
            same_bound = (model.mean_capacity_lower_bound(counts, model.BASE) ==
                          model.mean_capacity_lower_bound(counts, model.CANDIDATE))
            false_no_win += int(same_bound and 50 * b > 51 * c)
            gains.append(b / c)
        self.assertEqual(len(gains), 124)
        self.assertEqual(false_no_win, 50)
        self.assertEqual((min(gains), max(gains)), (1, 2))

    def test_300_unseen_randomized_instruction_multisets(self):
        rng = random.Random(31731102026)
        for _ in range(300):
            classes = tuple(rng.randrange(8) for _ in range(3))
            counts = tuple(rng.randrange(4) for _ in range(3))
            self.assertEqual(model.schedule_cycles(counts, classes),
                             matching_oracle(labeled_masks(counts, classes)))

    def test_strong_equal_resource_baseline_and_no_win_sensitivities(self):
        counts = (2, 2, 2)
        self.assertEqual(model.schedule_cycles(counts, model.BASE, issue=1), 6)
        self.assertEqual(model.schedule_cycles(counts, model.CANDIDATE, issue=1), 6)
        self.assertEqual(model.schedule_cycles(counts, model.BASE, ports=(2, 2, 2)), 3)
        self.assertEqual(model.schedule_cycles(counts, model.CANDIDATE, ports=(2, 2, 2)), 3)

    def test_exploratory_all_banks_slack_still_packing_limited(self):
        # NOT a preregistered holdout: four classes, including a zero-RF-read
        # instruction, show that the old per-bank no-win certificate applies
        # only to the fluid envelope, not necessarily atomic coissue IPC.
        counts = (2, 2, 2, 3)
        before_masks = model.BASE + (0,)
        after_masks = model.CANDIDATE + (0,)
        self.assertEqual(matching_oracle(labeled_masks(counts, before_masks)), 6)
        self.assertEqual(matching_oracle(labeled_masks(counts, after_masks)), 5)
        self.assertEqual(model.schedule_cycles(counts, before_masks), 6)
        self.assertEqual(model.schedule_cycles(counts, after_masks), 5)
        self.assertEqual(model.mean_capacity_lower_bound(counts, before_masks), 5)
        self.assertEqual(model.mean_capacity_lower_bound(counts, after_masks), 5)
        # All baseline bank demands are 4/9 per instruction, less than
        # 1/2 port/instruction at issue width two.
        self.assertEqual(
            [sum(n for n, m in zip(counts, before_masks) if m & (1 << b))
             for b in range(3)], [4, 4, 4])

    def test_fail_closed_input_and_no_hardware_claim(self):
        for counts, masks in [((1, 2), (1,)), ((-1,), (1,)), ((1,), (8,))]:
            with self.assertRaises(ValueError):
                model.schedule_cycles(counts, masks)
        with self.assertRaises(ValueError):
            model.schedule_cycles((1,), (1,), ports=(1, 0, 1))
        with self.assertRaises(ValueError):
            model.analyze((0, 0, 0))
        r = model.report()
        self.assertFalse(r["physical_gpu_measurements"])
        self.assertEqual(r["sweep_total_worlds"], 124)
        self.assertEqual(r["sweep_mean_false_no_win_worlds"], 50)


if __name__ == "__main__":
    unittest.main()
