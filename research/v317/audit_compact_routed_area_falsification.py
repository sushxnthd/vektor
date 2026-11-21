#!/usr/bin/env python3
"""Independent physical falsification of V317 pairwise-vs-compact area thesis.

Inputs are frozen routed values reported in PR #34 (2026-11-02).
These are NOT newly measured results. The analysis is conditional on the
published measurements and does not turn an electrically illegal route legal.
"""
from fractions import Fraction

COMPACT_AREA = Fraction("21314.6")
PAIRWISE_AREA = Fraction("21324.7")
COMPACT_HOLD = 6
COMPACT_MAX_CAP = 14
PAIRWISE_HOLD = 0
PAIRWISE_MAX_CAP = 21
MIN_SAVING = Fraction("0.02")

def evaluate(compact_area, pairwise_area, compact_violations, pairwise_violations):
    saving = (compact_area - pairwise_area) / compact_area
    legal = compact_violations == pairwise_violations == 0
    material = saving >= MIN_SAVING
    return {"saving": saving, "legal": legal,
            "material": material, "physical_win": legal and material}

def test():
    x = evaluate(COMPACT_AREA, PAIRWISE_AREA,
                 COMPACT_HOLD + COMPACT_MAX_CAP,
                 PAIRWISE_HOLD + PAIRWISE_MAX_CAP)
    assert x["saving"] == Fraction(-101, 213146)
    assert not x["legal"] and not x["material"] and not x["physical_win"]
    # Even assuming zero electrical violations, this measured area pair loses.
    assert not evaluate(COMPACT_AREA, PAIRWISE_AREA, 0, 0)["physical_win"]
    # A genuinely smaller, legal candidate is allowed by the independent test.
    assert evaluate(Fraction(100), Fraction(97), 0, 0)["physical_win"]
    # A smaller but illegal candidate must fail.
    assert not evaluate(Fraction(100), Fraction(97), 0, 1)["physical_win"]
    # Adding the same nonnegative tile overhead cannot reverse area dominance.
    for overhead in [0, 1, 1000, 1000000]:
        assert PAIRWISE_AREA + overhead > COMPACT_AREA + overhead
        for budget in [0, 10000, 50000, 1000000]:
            assert budget // (PAIRWISE_AREA + overhead) <= budget // (COMPACT_AREA + overhead)
    return x

if __name__ == "__main__":
    x = test()
    print("PASS: independent routed-area falsification and counterfactual controls")
    print("reported pairwise area saving (%):", float(100*x["saving"]))
    print("compact electrical violations:", COMPACT_HOLD + COMPACT_MAX_CAP)
    print("pairwise electrical violations:", PAIRWISE_HOLD + PAIRWISE_MAX_CAP)
    print("physical win:", x["physical_win"])
    print("Evidence tier: frozen PR #34 reported route; no new synthesis/STA")
