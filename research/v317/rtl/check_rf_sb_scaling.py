"""Independent software oracle for the V317 S/B bank-credit experiment.

This tests algorithmic semantics, not Verilog simulation or physical timing.
"""
import itertools
import json
import random


def oracle(valid, pairs, banks):
    reads = [0] * banks
    grants = []
    for enabled, (a, b) in zip(valid, pairs):
        ok = bool(enabled and reads[a] + (a == b) <= 1
                  and reads[b] + (a == b) <= 1)
        grants.append(ok)
        if ok:
            reads[a] += 1
            reads[b] += 1
    return tuple(grants)


def bankmask(valid, pairs, banks):
    once = [0] * banks
    twice = [0] * banks
    grants = []
    for enabled, (a, b) in zip(valid, pairs):
        ok = bool(enabled and ((a == b and not once[a])
                  or (a != b and not twice[a] and not twice[b])))
        grants.append(ok)
        if ok:
            if a == b:
                once[a] = twice[a] = 1
            else:
                twice[a] |= once[a]
                twice[b] |= once[b]
                once[a] = once[b] = 1
    return tuple(grants)


def pairwise(valid, pairs, banks):
    grants = []
    for i, (enabled, (a, b)) in enumerate(zip(valid, pairs)):
        prev = [bank for j, pair in enumerate(pairs[:i])
                if grants[j] for bank in pair]
        ok = bool(enabled and ((a == b and prev.count(a) == 0)
                  or (a != b and prev.count(a) < 2 and prev.count(b) < 2)))
        grants.append(ok)
    return tuple(grants)


def audit():
    exhaustive = 0
    for pairs in itertools.product(itertools.product(range(4), repeat=2), repeat=2):
        for valid in itertools.product((0, 1), repeat=2):
            expected = oracle(valid, pairs, 4)
            assert expected == bankmask(valid, pairs, 4) == pairwise(valid, pairs, 4)
            exhaustive += 1
    records = []
    for slots in (2, 4, 8):
        for banks in (4, 16, 64):
            rng = random.Random(317042 + slots * 100 + banks)
            for _ in range(2048):
                valid = [rng.getrandbits(1) for _ in range(slots)]
                pairs = [(rng.randrange(banks), rng.randrange(banks))
                         for _ in range(slots)]
                expected = oracle(valid, pairs, banks)
                assert expected == bankmask(valid, pairs, banks) == pairwise(valid, pairs, banks)
            records.append({"slots": slots, "banks": banks, "cases": 2048, "result": "PASS"})
    return {
        "tier": "INDEPENDENT_SOFTWARE_SEMANTICS_NOT_RTL",
        "exhaustive_S2_B4": exhaustive,
        "seeded_transfer": records,
        "generic_synthesis_measured": False,
        "physical_signoff": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
