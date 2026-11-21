"""V317 independent staged-bank operand service witnesses, synthetic only.

This tests the *assumption* that all operand banks must be read atomically.
It is not an NVIDIA operand collector, dynamic GPU model, or RTL evidence.
"""
from __future__ import annotations

from collections import Counter
from math import ceil
import unittest

BANKS = "ABC"
BASE = {"AB": "AB", "BC": "BC", "CA": "CA"}
CANDIDATE = {"AB": "A", "BC": "BC", "CA": "CA"}
COUNTS = {
    "atomic_predicted_win": (2, 2, 2),
    "atomic_predicted_no_win": (0, 3, 3),
    "prior_transfer": (2, 1, 3),
}

def instructions(counts, classes):
    return {f"{name}{j}": set(classes[name])
            for name, n in zip(("AB", "BC", "CA"), counts)
            for j in range(1, n + 1)}

def lower_bound(requests, issue=2):
    bank_reads = Counter(b for operands in requests.values() for b in operands)
    return max(ceil(len(requests) / issue), *(bank_reads[b] for b in BANKS))

def validate(requests, trace, issue=2):
    """Check each labeled instruction's reads, port occupancy and completions.

    Trace is a list of cycles, each a list of (instruction-id, bank) reads.
    Every bank has one read port; operands may be staged across cycles.
    """
    if not requests or issue <= 0:
        raise ValueError("nonempty requests and positive issue required")
    remaining = {i: set(operands) for i, operands in requests.items()}
    completed = set()
    if not trace:
        raise ValueError("missing trace")
    for cycle in trace:
        occupied = set()
        if not cycle:
            raise ValueError("empty cycle")
        for inst, bank in cycle:
            if inst not in remaining or bank not in BANKS:
                raise ValueError("unknown instruction/bank")
            if bank in occupied:
                raise ValueError("bank port oversubscribed")
            if bank not in remaining[inst]:
                raise ValueError("duplicate or unrequested read")
            occupied.add(bank)
            remaining[inst].remove(bank)
        just_completed = {i for i, operands in remaining.items()
                          if not operands and i not in completed}
        if len(just_completed) > issue:
            raise ValueError("completion width exceeded")
        completed.update(just_completed)
    if completed != set(requests):
        raise ValueError("unread operands")
    return len(trace)

def cycles(*rows):
    """Rows map physical bank A/B/C to a labeled instruction or '-'."""
    out = []
    for row in rows:
        assert len(row) == 3
        out.append(tuple((inst, bank) for inst, bank in zip(row, BANKS)
                         if inst != "-"))
    return tuple(out)

# Each witness is a feasible *optimal* schedule because it meets the
# independent bank-demand / issue lower bound. These are fixed examples.
WITNESSES = {
    "atomic_predicted_win": {
        "baseline": cycles(
            ("AB1", "AB1", "BC1"),
            ("AB2", "AB2", "BC2"),
            ("CA1", "BC1", "CA1"),
            ("CA2", "BC2", "CA2")),
        "candidate": cycles(
            ("AB1", "BC1", "BC1"),
            ("AB2", "BC2", "BC2"),
            ("CA1", "-", "CA1"),
            ("CA2", "-", "CA2")),
    },
    "atomic_predicted_no_win": {
        "baseline": cycles(
            ("-", "BC1", "BC1"),
            ("-", "BC2", "BC2"),
            ("-", "BC3", "BC3"),
            ("CA1", "-", "CA1"),
            ("CA2", "-", "CA2"),
            ("CA3", "-", "CA3")),
        "candidate": cycles(
            ("-", "BC1", "BC1"),
            ("-", "BC2", "BC2"),
            ("-", "BC3", "BC3"),
            ("CA1", "-", "CA1"),
            ("CA2", "-", "CA2"),
            ("CA3", "-", "CA3")),
    },
    "prior_transfer": {
        "baseline": cycles(
            ("AB1", "AB1", "BC1"),
            ("AB2", "AB2", "CA1"),
            ("CA1", "BC1", "CA2"),
            ("CA2", "-", "CA3"),
            ("CA3", "-", "-")),
        "candidate": cycles(
            ("AB1", "BC1", "BC1"),
            ("AB2", "-", "CA1"),
            ("CA1", "-", "CA2"),
            ("CA2", "-", "CA3"),
            ("CA3", "-", "-")),
    },
}

class StagedServiceFidelityAudit(unittest.TestCase):
    def test_frozen_witnesses_meet_lower_bound(self):
        expected = {
            "atomic_predicted_win": (4, 4),
            "atomic_predicted_no_win": (6, 6),
            "prior_transfer": (5, 5),
        }
        for regime, counts in COUNTS.items():
            observed = []
            for policy, classes in (("baseline", BASE), ("candidate", CANDIDATE)):
                req = instructions(counts, classes)
                trace = WITNESSES[regime][policy]
                measured = validate(req, trace)
                self.assertEqual(measured, lower_bound(req))
                observed.append(measured)
            self.assertEqual(tuple(observed), expected[regime])
            self.assertEqual(observed[0] / observed[1], 1.0)

    def test_atomic_model_comparison_only(self):
        # The staged checker never calls the atomic optimizer.
        from research.v317.bank_coissue_hypergraph import analyze
        self.assertEqual([analyze(x)["gain"] for x in COUNTS.values()],
                         [1.5, 1.0, 1.2])

    def test_independent_validator_rejects_bad_physical_traces(self):
        req = instructions((1, 1, 0), BASE)
        good = cycles(("AB1", "AB1", "BC1"),
                      ("-", "BC1", "-"))
        self.assertEqual(validate(req, good), 2)
        bad_traces = (
            cycles(("AB1", "AB1", "BC1")),  # missing BC1 B
            ((("AB1", "A"), ("AB1", "A")),),  # duplicate read/port
            ((("AB1", "A"), ("BC1", "A")),),  # bank conflict
            ((("AB1", "A"), ("AB1", "B"), ("BC1", "C")),
             (("BC1", "B"), ("BC1", "C"))),  # duplicate C
            ((("UNKNOWN", "A"),),),  # invented instruction
        )
        for trace in bad_traces:
            with self.subTest(trace=trace), self.assertRaises(ValueError):
                validate(req, trace)

    def test_single_completion_slot_rejects_two_finishes(self):
        req = instructions((1, 1, 0), CANDIDATE)
        trace = cycles(("AB1", "BC1", "BC1"))
        with self.assertRaisesRegex(ValueError, "completion width"):
            validate(req, trace, issue=1)

if __name__ == "__main__":
    unittest.main()
