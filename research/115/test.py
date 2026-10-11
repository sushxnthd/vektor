import unittest
from trace_model import *

class Tests(unittest.TestCase):
    def test_naive_reorder_counterexample(self):
        req=[Req(0,9,2,1,4096),Req(1,9,2,1,8192)]
        pages={1:8,2:9}
        events=paired_trace(req,pages,req[::-1])
        bad=naive_fifo(req,events)
        self.assertEqual(sum(x.pa!=translate(req[x.rid],pages) for x in bad),2)
        self.assertTrue(all(x.pa==translate(req[x.rid],pages) for x in events))
    def test_one_line_eight_lanes(self):
        self.assertEqual(len(aggregate_lanes([0,4,8,12,16,20,24,28])),1)
    def test_two_lines(self):
        self.assertEqual(len(aggregate_lanes([0,28,32,60])),2)
    def test_reject_cross_page(self):
        with self.assertRaises(ValueError):translate(Req(0,0,0,0,4095,4),{0:1,1:2})
    def test_discovery(self):
        x=sample(115001,256)
        self.assertGreater(x['naive_misattributed_records'],0)
        self.assertEqual(x['paired_misattributed_records'],0)
    def test_holdout(self):
        x=sample(115002,128)
        self.assertGreater(x['coalesced_cases'],0)
        self.assertEqual(x['paired_misattributed_records'],0)

if __name__=='__main__':unittest.main()
