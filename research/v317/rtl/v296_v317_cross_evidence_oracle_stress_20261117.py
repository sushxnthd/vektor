#!/usr/bin/env python3
"""Cross-evidence optimistic no-go audit; NOT a matched V296 measurement.

Frozen inputs come from distinct experiments: V296 decoded Nangate45 mapped
area (2026-10-26) and V317 four-slot instantaneous bank-service oracle
(2026-11-02). Their combination is a *conditional stress test*, not a valid
cross-design performance estimate. It asks what follows IF the candidate
inherits the V296 area ratio and cannot exceed the stated oracle service ratio.
"""
from fractions import Fraction as Q

PAIR_AREA = Q("10426.402")
SERIAL_AREA = Q("10143.112")
AREA_RATIO = PAIR_AREA / SERIAL_AREA
ORACLE = {
    "uniform_16bank": Q("1.001025"),
    "samebank_70pct": Q("1.002278"),
    "uniform_4bank": Q("1.046683"),
    "hotbank_65pct": Q("1.099869"),
    "constructed_head_blocker": Q("1.500"),
    "disjoint_control": Q("1.000"),
}
def max_clock_ratio_for_area_normalized_win(oracle_ratio):
    return oracle_ratio / AREA_RATIO

def classify(oracle_ratio, clock_ratio=Q(1)):
    # strict >: equality is parity, not a positive win
    return oracle_ratio > AREA_RATIO * clock_ratio

def run():
    assert PAIR_AREA > SERIAL_AREA
    assert not classify(ORACLE["uniform_16bank"])
    assert not classify(ORACLE["samebank_70pct"])
    assert classify(ORACLE["uniform_4bank"])
    assert classify(ORACLE["hotbank_65pct"])
    assert not classify(ORACLE["disjoint_control"])
    assert not classify(ORACLE["uniform_16bank"], Q("0.98"))
    assert classify(ORACLE["uniform_4bank"], Q("1.01"))
    assert not classify(ORACLE["uniform_4bank"], Q("1.05"))
    print("CONDITIONAL cross-evidence stress test: incompatible designs; no physical signoff")
    print("V296 decoded area ratio", float(AREA_RATIO))
    for regime, bound in ORACLE.items():
        clock_ceiling = max_clock_ratio_for_area_normalized_win(bound)
        print(regime, "oracle service", float(bound),
              "max candidate/reference clock-period ratio for positive TP/area",
              round(float(clock_ceiling), 8),
              "equal-clock optimistic verdict",
              "POSSIBLE_ONLY" if classify(bound) else "NO_GO")
    print("A possible-only verdict does not establish a realizable scheduler.")
    print("Requires matched same-design RTL, routed electrical legality, workload cycles and ports.")
if __name__ == "__main__":
    run()
