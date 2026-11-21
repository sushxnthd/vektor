#!/usr/bin/env python3
"""Executable negative control for V317 matched-trace resource identity.

The current compare() accepts replay summaries with unequal physical storage
budgets because audit() omits word_budget from its returned summary. This
regression intentionally demonstrates the acceptance; it is not RTL evidence.
"""
import importlib.util
from pathlib import Path
import tempfile

def main():
    source = Path(__file__).with_name("v317_matched_trace_gate.py")
    spec = importlib.util.spec_from_file_location("v317_trace_gate", source)
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    gate.selftest()
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "same.csv"
        p.write_text("cycle,request_id,bank,operand,complete,retained_words\n"
                     "0,0,0,0,0,1\n1,0,1,1,1,0\n")
        kw = dict(period_ns=3, bank_ports=1, return_ports=1,
                  max_cycles=2, retention_mode="registered")
        baseline = gate.audit(p, word_budget=2, **kw)
        candidate = gate.audit(p, word_budget=8, **kw)
        assert "word_budget" not in baseline and "word_budget" not in candidate
        result = gate.compare(baseline, candidate)
        assert result["ratio"] == 1.0
        print("CONFIRMED: unequal 2-word/8-word hardware passes equal-resource compare")
        print("REQUIRED: propagate word_budget and retention_mode to summaries; "
              "compare both and reject mismatches before calculating throughput")
    print("PASS: negative control reproduced")

if __name__ == "__main__":
    main()
