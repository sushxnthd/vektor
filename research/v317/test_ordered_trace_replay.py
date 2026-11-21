#!/usr/bin/env python3
"""Regression and falsification checks for ordered trace replay.

Run: python3 -m unittest discover -s research/v317 -p 'test_ordered_trace_replay.py'
No synthetic example is represented as a real GPU trace.
"""
import importlib.util
import pathlib
import unittest

SOURCE = pathlib.Path(__file__).with_name("ordered_trace_fail_closed_replay.py")
spec = importlib.util.spec_from_file_location("ordered_replay", SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def req(i, *banks):
    return {"id": i, "banks": list(banks)}

def rows(*cycles):
    return [{"cycle": t, "requests": list(c)} for t, c in enumerate(cycles)]

class ReplayRegression(unittest.TestCase):
    def test_head_blocking_must_not_bypass(self):
        # Two requests to bank zero use both ports; third request is blocked.
        # A request to bank one behind the blocked head is NOT FIFO-eligible.
        trace = rows([req("a",0), req("b",0), req("c",0), req("d",1)])
        fifo = mod.replay(trace, 2, 2, 4, 4, "fifo")
        greedy = mod.replay(trace, 2, 2, 4, 4, "greedy")
        self.assertEqual(fifo["completed"], 2)
        self.assertEqual(greedy["completed"], 3)
        self.assertEqual(fifo["backlog"], 2)
        self.assertEqual(greedy["backlog"], 1)

    def test_duplicate_operands_consume_two_ports(self):
        trace = rows([req("a",0,0),req("b",0)])
        self.assertEqual(mod.replay(trace,1,2,2,2,"greedy")["completed"],1)

    def test_unschedulable_duplicate_operand_fails_closed(self):
        trace = rows([req("impossible",0,0),req("valid",1)])
        for policy in ("fifo","greedy"):
            with self.assertRaisesRegex(ValueError, "unschedulable request"):
                mod.replay(trace,2,1,2,2,policy)
        # Two physical ports permit the duplicate operand.
        self.assertEqual(mod.replay(trace,2,2,2,2,"fifo")["completed"],2)

    def test_shared_output_cap(self):
        trace = rows([req("a",0),req("b",1)])
        for policy in ("fifo","greedy"):
            self.assertEqual(mod.replay(trace,2,2,2,1,policy)["completed"],1)

    def test_zero_resource_rejected(self):
        with self.assertRaises(ValueError):
            mod.replay(rows([req("a",0)]),1,0,1,1,"fifo")

    def test_greedy_is_not_an_upper_bound(self):
        # Same bank ports, slots, and output capacity for both policies.
        # Greedy takes (0,1) first and completes one; optimal packing
        # chooses (0) and (1), completing two. This is a falsification
        # of the earlier claim that greedy is a throughput upper bound.
        from itertools import combinations
        trace = rows([req("a",0,1),req("b",0),req("c",1)])
        greedy = mod.replay(trace,2,1,2,2,"greedy")["completed"]
        requests = trace[0]["requests"]
        optimum = max(
            (len(choice) for k in range(3)
             for choice in combinations(requests,k)
             if all(sum(r["banks"].count(b) for r in choice)<=1
                    for b in (0,1))),
            default=0)
        self.assertEqual(greedy,1)
        self.assertEqual(optimum,2)
        self.assertLess(greedy,optimum)

    def test_conservation_exhaustive(self):
        from itertools import product
        for n in range(5):
            for sequence in product(range(2), repeat=n):
                trace=rows([req(i,b) for i,b in enumerate(sequence)])
                for ports in (1,2):
                    for slots in (1,2,3):
                        for out in (1,2):
                            for policy in ("fifo","greedy"):
                                result=mod.replay(trace,2,ports,slots,out,policy)
                                self.assertEqual(result["arrivals"],result["completed"]+result["backlog"])
                                self.assertLessEqual(result["completed"],min(slots,out))
if __name__=="__main__":
    unittest.main()
