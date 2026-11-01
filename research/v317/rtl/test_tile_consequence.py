"""Independent integer-tile and finite-workload checks of the V317 boundary."""
import math
import random
import unittest
from dataclasses import replace

from research.v317.rtl.tile_consequence import Case, evaluate, frozen_cases


def count_tiles_by_enumeration(budget, other, arb):
    n = 0
    while (n + 1) * (other + arb) <= budget + 1e-8:
        n += 1
    return n


def finite_workload(c: Case, area: float, delay: float, wire: float, steps=10000):
    """Independent integer-token executor with infinite queue and finite horizon.

    One tick = 1 ns. Fractional compute, arrival, bandwidth tokens carry over;
    no speculative speedup from grant changes or extra register-bank ports.
    """
    tiles = count_tiles_by_enumeration(c.budget, c.other_area, area)
    period = max(c.other_delay, delay + wire)
    capacity = tiles * c.work_per_tile_cycle / period
    arrived_fraction = bandwidth_fraction = compute_fraction = 0.0
    queue = completed = 0
    for _ in range(steps):
        arrived_fraction += c.offered
        bandwidth_fraction += c.bandwidth
        compute_fraction += capacity
        incoming = math.floor(arrived_fraction + 1e-9)
        arrived_fraction -= incoming
        queue += incoming
        bw = math.floor(bandwidth_fraction + 1e-9)
        comp = math.floor(compute_fraction + 1e-9)
        served = min(queue, bw, comp)
        queue -= served
        bandwidth_fraction -= served
        compute_fraction -= served
        # No indefinite stockpiling of service tokens during idle intervals.
        bandwidth_fraction = min(bandwidth_fraction, c.bandwidth)
        compute_fraction = min(compute_fraction, capacity)
        completed += served
    return completed / steps


class TestFrozen(unittest.TestCase):
    def test_frozen_predictions(self):
        a, b, c, d, e = [evaluate(x) for x in frozen_cases()]
        self.assertEqual((a['source']['tiles'], a['pairwise']['tiles']), (24, 24))
        self.assertEqual(a['gain'], 1.0)
        self.assertEqual((b['source']['tiles'], b['pairwise']['tiles']), (24, 25))
        self.assertGreater(b['gain'], 1.04)
        self.assertEqual(c['gain'], 1.0)
        self.assertGreater(d['gain'], 1.5)
        self.assertLessEqual(e['gain'], 1.0)

    def test_unseen_deterministic_holdouts(self):
        rng = random.Random(31720261101)
        for i in range(64):
            c = Case(
                name=f'unseen_{i}',
                budget=rng.uniform(300_000, 2_000_000),
                other_area=rng.uniform(20_000, 60_000),
                other_delay=rng.uniform(0.5, 2.5),
                source_wire=rng.uniform(0, 0.8),
                pair_wire=rng.uniform(0, 0.8),
                offered=rng.uniform(1, 100),
                bandwidth=rng.uniform(1, 60),
                work_per_tile_cycle=rng.uniform(0.2, 2.0),
            )
            r = evaluate(c)
            for label, area, delay, wire in [
                ('source', c.source_area, c.source_delay, c.source_wire),
                ('pairwise', c.pair_area, c.pair_delay, c.pair_wire),
            ]:
                self.assertEqual(r[label]['tiles'], count_tiles_by_enumeration(c.budget, c.other_area, area))
                observed = finite_workload(c, area, delay, wire)
                expected = r[label]['throughput_work_per_ns']
                self.assertAlmostEqual(observed, expected, delta=0.03, msg=f'{c.name}/{label}')

    def test_same_clock_same_tiles_same_service(self):
        c = frozen_cases()[0]
        r = evaluate(c)
        self.assertEqual(r['source']['tiles'], r['pairwise']['tiles'])
        self.assertEqual(r['source']['period_ns'], r['pairwise']['period_ns'])
        self.assertEqual(r['gain'], 1.0)

    def test_bandwidth_cap_cannot_increase_gain_when_both_saturated(self):
        c = frozen_cases()[1]
        for b in (0.5, 1, 4, 8, 12, 16):
            self.assertEqual(evaluate(replace(c, bandwidth=b))['gain'], 1.0)

    def test_invalid_inputs_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(replace(frozen_cases()[0], pair_wire=-0.1))
        with self.assertRaises(ValueError):
            evaluate(replace(frozen_cases()[0], other_area=0))


if __name__ == '__main__':
    unittest.main()
