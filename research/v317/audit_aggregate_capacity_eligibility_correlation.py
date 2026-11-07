#!/usr/bin/env python3
"""Falsify an aggregate-rate times eligible-cycle ceiling.

A mean capacity across ALL cycles cannot generally be multiplied by the
fraction of eligible cycles: capacity can concentrate in eligible cycles.
This is independent of the earlier occupancy/control overlap problem.

All rates are requests/cycle. This is a synthetic mathematical audit, NOT
GPU/RTL evidence. A valid trace upper bound is the sum of per-cycle minimum
resource capacities, masked by global eligibility. An aggregate upper bound
is min(sum bank, sum issue, sum output, sum memory, sum eligible*peak),
provided each capacity is a justified upper bound on actual service.
"""
from itertools import product

def exact_upper(eligible, resources):
    if not resources or any(len(r) != len(eligible) for r in resources):
        raise ValueError("matched nonempty resource traces required")
    if any(type(x) is not bool for x in eligible):
        raise ValueError("eligibility must be Boolean")
    if any(type(v) is not int or v < 0 for r in resources for v in r):
        raise ValueError("nonnegative integer capacities required")
    n = len(eligible)
    return sum(min(r[t] for r in resources) if eligible[t] else 0
               for t in range(n)) / n

def aggregate_upper(eligible, resources):
    n = len(eligible)
    # Each resource total is an independently valid total-service ceiling.
    return min(sum(r) for r in resources) / n

def invalid_product(eligible, resources):
    return aggregate_upper(eligible, resources) * (sum(eligible)/len(eligible))

def run():
    # Half the cycles are eligible; every unit of capacity is on those cycles.
    eligible = (True, False, True, False)
    resources = ((2, 0, 2, 0),) * 4
    actual = exact_upper(eligible, resources)
    naive = invalid_product(eligible, resources)
    assert actual == 1.0 and naive == 0.5 and aggregate_upper(eligible, resources) == 1.0
    checked = 0
    violations = 0
    # Independent exhaustive enumeration of small traces: exact per-cycle
    # service cannot exceed any whole-horizon resource capacity.
    for e in product((False, True), repeat=3):
        for a in product(range(3), repeat=3):
            for b in product(range(3), repeat=3):
                r = (a, b)
                exact = exact_upper(e, r)
                assert exact <= aggregate_upper(e, r) + 1e-12
                if exact > invalid_product(e, r) + 1e-12:
                    violations += 1
                checked += 1
    assert violations > 0
    print({"status": "PASS", "cases": checked, "false_ceiling_cases": violations,
           "counterexample_actual": actual, "invalid_product_ceiling": naive,
           "valid_aggregate_ceiling": aggregate_upper(eligible, resources),
           "interpretation": "Aggregate average capacities cannot be multiplied by eligibility without a per-eligible-cycle capacity bound. No hardware claim."})

if __name__ == "__main__":
    run()
