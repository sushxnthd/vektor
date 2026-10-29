"""Independent value-carrying coherence oracle for V303.

This checker does not import the V-Tile simulator. It validates the semantic
requirement that a cache hit after a register write must see the new version.
"""
from itertools import product
import json


def check(policy, operations, capacity=2):
    rf = {0: 10, 1: 20}
    cache = {}
    for op, reg in operations:
        if op == "read":
            if reg in cache:
                observed = cache[reg]
            else:
                observed = rf[reg]
                if len(cache) >= capacity and reg not in cache:
                    cache.pop(next(iter(cache)))
                cache[reg] = observed
            if observed != rf[reg]:
                return False
        elif op == "write":
            rf[reg] += 1
            if policy == "invalidate":
                cache.pop(reg, None)
            elif policy == "ideal_update":
                if reg in cache:
                    cache[reg] = rf[reg]
            elif policy == "implicit_preserve":
                pass
            else:
                raise ValueError(policy)
        else:
            raise ValueError(op)
    return True


def run():
    alphabet = [("read", 0), ("read", 1), ("write", 0), ("write", 1)]
    counts = {}
    examples = {}
    for policy in ("invalidate", "ideal_update", "implicit_preserve"):
        bad = 0
        for length in range(1, 6):
            for seq in product(alphabet, repeat=length):
                if not check(policy, seq):
                    bad += 1
                    examples.setdefault(policy, seq)
        counts[policy] = bad
    assert counts["invalidate"] == counts["ideal_update"] == 0
    assert counts["implicit_preserve"] > 0
    return {"checked_sequences": sum(4**n for n in range(1, 6)),
            "violations_by_policy": counts,
            "first_implicit_preserve_counterexample": examples["implicit_preserve"]}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
