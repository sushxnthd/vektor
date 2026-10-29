"""Hand-calculated completion tests for the V305 admission model."""
import unittest
from simulator import Request, simulate, make_trace

class TestV305(unittest.TestCase):
    def test_one_request_latency(self):
        for policy in ('fifo','rr','fixed','shortest','guard'):
            x = simulate([Request(0,0,0)], (3,3,3,3), policy)
            self.assertEqual((x['cycles'], x['completed'], x['p99']), (4,1,4))
    def test_two_partitions_parallel(self):
        trace = [Request(0,0,0),Request(1,0,1)]
        for policy in ('fifo','rr','fixed','shortest','guard'):
            x = simulate(trace, (3,3,3,3), policy)
            self.assertEqual((x['cycles'], x['completed']), (4,2))
    def test_one_partition_response_port(self):
        trace = [Request(0,0,0),Request(1,0,0)]
        for policy in ('fifo','rr','fixed','shortest','guard'):
            x = simulate(trace, (3,3,3,3), policy)
            self.assertEqual((x['cycles'], x['completed']), (5,2))
    def test_no_request(self):
        for policy in ('fifo','rr','fixed','shortest','guard'):
            x = simulate([], (3,3,3,3), policy)
            self.assertEqual((x['cycles'],x['completed']), (0,0))
    def test_conservation_and_repeatability(self):
        for seed in (1,2,3):
            trace, lat = make_trace(seed, 'W1', duration=45)
            for policy in ('fifo','rr','fixed','shortest','guard'):
                a = simulate(trace,lat,policy,mshr=8,ingress=8)
                b = simulate(trace,lat,policy,mshr=8,ingress=8)
                self.assertEqual(a,b)
                self.assertEqual(a['completed'],len(trace))
                self.assertEqual(sum(a['partition_completed']),len(trace))

if __name__ == '__main__': unittest.main()
