"""Independent directed checks of frozen V317 write-visibility protocol."""
import unittest
from itertools import product
from research.v317.write_visibility_latency import (Write, exhaustive_audit,
    grant_from_monitor, grant_with_source_barrier, oracle_value_safe)

class WriteVisibilityTests(unittest.TestCase):
    def test_late_write_stale(self):
        w = (Write(0,2,1,True), Write(1,0,0,False))
        self.assertTrue(grant_from_monitor(1,1,w,2,1))
        self.assertFalse(oracle_value_safe(1,1,w))
        self.assertFalse(grant_with_source_barrier(1,1,w,2,1))

    def test_zero_latency_exhaustive_masks(self):
        for req,cap,m0,m1,h0,h1 in product(range(4),range(4),range(4),range(4),(False,True),(False,True)):
            w=(Write(0,2,m0,h0),Write(1,2,m1,h1))
            self.assertEqual(grant_from_monitor(cap,req,w,2,0),oracle_value_safe(cap,req,w))

    def test_unrelated_write_conservative_cost(self):
        w=(Write(0,2,2,True),Write(1,0,0,False))
        self.assertTrue(oracle_value_safe(3,1,w))
        self.assertFalse(grant_with_source_barrier(3,1,w,2,2))

    def test_wrong_namespace_conservative_cost(self):
        w=(Write(0,2,1,False),Write(1,0,0,False))
        self.assertTrue(oracle_value_safe(1,1,w))
        self.assertFalse(grant_with_source_barrier(1,1,w,2,1))

    def test_delivered_dirty_write(self):
        w=(Write(0,1,1,True),Write(1,0,0,False))
        self.assertFalse(grant_from_monitor(1,1,w,3,2))
        self.assertFalse(grant_with_source_barrier(1,1,w,3,2))

    def test_frozen_sweep(self):
        result=exhaustive_audit()
        self.assertGreater(result['total_worlds'],80000)
        for row in result['summary']:
            self.assertEqual(row['barrier_unsafe_grants'],0)
            self.assertEqual(row['naive_unsafe_grants']==0,row['latency']==0)

if __name__=='__main__': unittest.main()
