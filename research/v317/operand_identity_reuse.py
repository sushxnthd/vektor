"""Exact synthetic operand-identity sharing challenge for V317.

No physical register-bank mapping, RF-cache inference, functional read elimination,
or measured GPU throughput is implied. Each instruction is initially ready.
"""
from functools import lru_cache


def make_instructions(a, b, shared, candidate=False):
    """Return labeled tuples of (bank, register-identity) operands."""
    if min(a, b, shared) < 0 or shared > min(a, b):
        raise ValueError("invalid counts or shared pairs")
    rows = []
    for i in range(a):
        reads = (("A", f"A{i}"),)
        if not candidate:
            reads += (("B", f"S{i}" if i < shared else f"UA{i}"),)
        rows.append((f"AB{i}", reads))
    for j in range(b):
        reads = (("B", f"S{j}" if j < shared else f"UB{j}"),
                 ("C", f"C{j}"))
        rows.append((f"BC{j}", reads))
    return tuple(rows)


def legal_cycle(rows, indices, k):
    """One atomic service cycle: one distinct register value read per bank."""
    if not (1 <= len(indices) <= min(2, k)) or len(set(indices)) != len(indices):
        return False
    bank_values = {}
    for i in indices:
        if i < 0 or i >= len(rows):
            return False
        for bank, identity in rows[i][1]:
            if bank in bank_values and bank_values[bank] != identity:
                return False
            bank_values[bank] = identity
    return True


def exact_matching_schedule(rows, k):
    """Optimal schedule via maximum-cardinality matching, not via the law."""
    if k < 1:
        raise ValueError("K must be positive")
    n = len(rows)

    @lru_cache(None)
    def optimum(mask):
        if mask == 0:
            return 0, ()
        i = (mask & -mask).bit_length() - 1
        left = mask ^ (1 << i)
        best_n, best = optimum(left)
        best_n, best = best_n + 1, ((i,),) + best
        for j in range(i + 1, n):
            if (left & (1 << j)) and legal_cycle(rows, (i, j), k):
                pair_n, pair_schedule = optimum(left ^ (1 << j))
                if pair_n + 1 < best_n:
                    best_n, best = pair_n + 1, ((i, j),) + pair_schedule
        return best_n, best

    cycles, witness = optimum((1 << n) - 1)
    validate_witness(rows, witness, k)
    return cycles, witness


def validate_witness(rows, schedule, k):
    seen = set()
    for cycle in schedule:
        if not legal_cycle(rows, cycle, k):
            raise AssertionError("illegal bank/identity/collector service")
        for idx in cycle:
            if idx in seen:
                raise AssertionError("instruction serviced twice")
            seen.add(idx)
    if seen != set(range(len(rows))):
        raise AssertionError("missing instruction")
    return True


def independent_partition_optimum(rows, k):
    """Independent exact set-partition search; does not call matching or legal_cycle."""
    if k < 1:
        raise ValueError("K must be positive")
    n = len(rows)
    best = n

    def search(remaining, used):
        nonlocal best
        if not remaining:
            best = min(best, used)
            return
        if used >= best:
            return
        i = remaining[0]
        search(remaining[1:], used + 1)
        if k >= 2:
            for pos in range(1, len(remaining)):
                j = remaining[pos]
                vals = {}
                compatible = True
                for ix in (i, j):
                    for bank, ident in rows[ix][1]:
                        if bank in vals and vals[bank] != ident:
                            compatible = False
                        vals[bank] = ident
                if compatible:
                    search(remaining[1:pos] + remaining[pos+1:], used + 1)

    search(tuple(range(n)), 0)
    return best


def predicted_cycles(a, b, shared, k):
    if min(a, b, shared) < 0 or shared > min(a, b) or a+b == 0 or k < 1:
        raise ValueError("invalid workload")
    n = a + b
    return (n, n) if k == 1 else (n - shared, max(a, b))


def evaluate(a, b, shared, k):
    result = []
    for cand in (False, True):
        rows = make_instructions(a, b, shared, candidate=cand)
        cycles, witness = exact_matching_schedule(rows, k)
        result.append((cycles, witness))
    return tuple(result)


def margin_with_overhead(a, b, shared, k, extra_cycles=0.0, clock_penalty=0.0):
    if extra_cycles < 0 or clock_penalty < 0:
        raise ValueError("nonnegative overhead required")
    t0, t1 = predicted_cycles(a, b, shared, k)
    return t0 / ((t1 + extra_cycles) * (1 + clock_penalty))
