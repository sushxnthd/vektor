"""Independent V317 tests: frozen predictions, occupancy and queue semantics."""
import unittest
from integrated_occupancy_boundary import (
    ROWS, REGIMES, count_tiles, robust_25_vs_24_interval,
    occupancy_boundary, fluid_rate, instantaneous_rate, simulate, period_ns
)

class BoundaryTests(unittest.TestCase):
    def test_robust_interval_and_outside(self):
        low, high = robust_25_vs_24_interval()
        self.assertEqual((low,high), (1165226,1184191))
        for r in ROWS:
            for b in (low,1175000,high):
                self.assertEqual((count_tiles(b,r.source_area),
                                  count_tiles(b,r.pair_area)),(24,25))
        self.assertTrue(any(count_tiles(low-1,r.pair_area)<25 for r in ROWS))
        self.assertTrue(any(count_tiles(high+1,r.source_area)>=25 for r in ROWS))

    def test_frozen_fluid_predictions_all_rows(self):
        for r in ROWS:
            gains = [fluid_rate(r,c,True)/fluid_rate(r,c,False) for c in REGIMES]
            self.assertAlmostEqual(gains[0],25/24)
            self.assertAlmostEqual(gains[1],1)
            self.assertLess(gains[2],1)
            self.assertAlmostEqual(gains[3],1)
            self.assertGreater(gains[4],1)
            self.assertAlmostEqual(occupancy_boundary(r,REGIMES[0]),24/25)

    def test_generous_source_repair_does_not_change_common_tile_clock(self):
        for r in ROWS:
            self.assertEqual(period_ns(r,False,2.2,False),
                             period_ns(r,False,2.2,True))

    def test_unqueued_bandwidth_falsifies_fluid_no_win(self):
        c,r=REGIMES[1],ROWS[0]
        ns,np=count_tiles(c.budget,r.source_area),count_tiles(c.budget,r.pair_area)
        ts,tp=period_ns(r,False),period_ns(r,True)
        self.assertAlmostEqual(fluid_rate(r,c,True)/fluid_rate(r,c,False),1)
        clipped=instantaneous_rate(np,c.pair_occupancy,tp,c.bandwidth)/(
                instantaneous_rate(ns,c.source_occupancy,ts,c.bandwidth))
        self.assertGreater(clipped,1.005)

    def test_unseen_activity_streams_against_exact_clipping(self):
        for seed,n,u,bw in ((401,24,.75,8),(877,25,.75,8),
                            (211,24,.55,7),(903,25,.81,11)):
            observed=simulate(n,u,2.2,bw,seed=seed,cycles=120000)
            predicted=instantaneous_rate(n,u,2.2,bw)
            self.assertLess(abs(observed-predicted),.025)

    def test_backlog_recovers_fluid_bandwidth_cap(self):
        for n in (24,25):
            observed=simulate(n,.75,2.2,8,seed=91,cycles=120000,backlog=True)
            self.assertLess(abs(observed-8),.01)

if __name__ == '__main__':
    unittest.main()
