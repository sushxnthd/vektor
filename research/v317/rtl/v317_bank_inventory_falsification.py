#!/usr/bin/env python3
"""Falsification: matched service checker must account for finite bank inventory.
This is source-level checker validation, NOT RTL or physical timing evidence.
"""
import tempfile
from pathlib import Path
from v317_matched_trace_gate import audit, compare

def main():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"trace.csv"
        p.write_text("cycle,request_id,bank,operand,complete,retained_words\n0,0,2,0,0,1\n")
        try:
            audit(p,period_ns=3,bank_ports=1,return_ports=1,word_budget=2,max_cycles=1,bank_count=2)
        except (ValueError,TypeError):
            pass
        else:
            raise AssertionError("checker accepted a third bank in a two-bank design")
        # The present checker has no bank_count parameter: TypeError above is
        # NOT a pass. Require explicit inventory support before claiming repair.
        import inspect
        if "bank_count" not in inspect.signature(audit).parameters:
            raise AssertionError("bank inventory absent from physical audit API")
    print("PASS: finite physical bank inventory enforced")

if __name__=="__main__":
    main()
