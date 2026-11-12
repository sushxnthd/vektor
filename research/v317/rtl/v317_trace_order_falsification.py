#!/usr/bin/env python3
"""Regression/falsification of V317 matched trace gate's row-order dependence.

This is a checker correctness test, NOT RTL simulation or physical evidence.
A cycle is a set of simultaneous grants; CSV row order must not affect validity.
"""
import csv
import tempfile
from pathlib import Path
from v317_matched_trace_gate import audit

HEADER = "cycle,request_id,bank,operand,complete,retained_words\n"
# Both operands are granted in cycle zero; the completion flag is attached to
# operand zero. Reversing the rows must not change a simultaneous transaction.
ROWS = [
    "0,7,0,0,1,0\n",
    "0,7,1,1,0,0\n",
]

def evaluate(rows):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "trace.csv"
        path.write_text(HEADER + "".join(rows))
        try:
            return ("accept", audit(path, period_ns=3, bank_ports=1,
                                    return_ports=1, word_budget=0, max_cycles=1)["completed"])
        except ValueError as exc:
            return ("reject", str(exc))

def main():
    first = evaluate(ROWS)
    reverse = evaluate(list(reversed(ROWS)))
    assert first != reverse, (first, reverse)
    assert first[0] == "reject" and reverse == ("accept", 1), (first, reverse)
    print("FALSIFIED: identical simultaneous grants differ by CSV row order")
    print("original:", first)
    print("reversed:", reverse)
    print("Repair: collect all cycle grants, then validate completion against post-grant state;")
    print("do not infer combinational timing or zero-register bypass from row order.")

if __name__ == "__main__":
    main()
