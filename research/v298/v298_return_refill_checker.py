#!/usr/bin/env python3
"""V298 event-order and liveness falsification (controller-level only).

Independent of the RTL implementation. This is not GPU throughput evidence.
free_count is post-return, pre-admission. This checker deliberately detects
the original registered-guard-only same-cycle refill race.
"""
from itertools import product


def reference(policy, guard, free, ready, bg, returned, dependent, cancel, oracle):
    crit_issue = bool(free and ready)
    effective_guard = bool(not cancel and (guard or (returned and dependent)))
    last = free == 1
    block = (policy == 1 and last or
             policy == 2 and last and effective_guard or
             policy == 3 and last and effective_guard and not oracle)
    bg_issue = bool(free and not ready and bg and not block)
    next_guard = False if crit_issue or cancel else (
        True if returned and dependent else bool(guard))
    return crit_issue, bg_issue, next_guard


def original_rtl(policy, guard, free, ready, bg, returned, dependent, cancel, oracle):
    crit_issue = bool(free and ready)
    last = free == 1
    block = (policy == 1 and last or
             policy == 2 and last and guard or
             policy == 3 and last and guard and not oracle)
    bg_issue = bool(free and not ready and bg and not block)
    next_guard = False if crit_issue or cancel else (
        True if returned and dependent else bool(guard))
    return crit_issue, bg_issue, next_guard


def corrected_rtl_equation(policy, guard, free, ready, bg, returned, dependent, cancel, oracle):
    # Algebraically independent implementation: select reservation first.
    pending = (guard or (returned and dependent)) and not cancel
    reserved = ((policy == 1) or
                (policy == 2 and pending) or
                (policy == 3 and pending and not oracle))
    ci = free > 0 and ready
    bi = free > 0 and bg and not ready and not (free == 1 and reserved)
    nq = (not (ci or cancel)) and (returned and dependent or guard)
    return bool(ci), bool(bi), bool(nq)


def run():
    checks = 0
    old_failures = 0
    for policy, guard, free, ready, bg, returned, dep, cancel, oracle in product(
            range(4), range(2), range(5), *([range(2)] * 6)):
        expected = reference(policy, guard, free, ready, bg, returned, dep, cancel, oracle)
        actual = corrected_rtl_equation(policy, guard, free, ready, bg, returned, dep, cancel, oracle)
        assert expected == actual, (policy, guard, free, ready, bg, returned, dep, cancel, oracle)
        if original_rtl(policy, guard, free, ready, bg, returned, dep, cancel, oracle) != expected:
            old_failures += 1
        checks += 1
    assert checks == 2560
    assert old_failures > 0, "Negative control failed to detect old RTL race"
    # At the exact return edge the old RTL erroneously fills the sole credit.
    case = (2, 0, 1, 0, 1, 1, 1, 0, 0)
    assert reference(*case)[1] is False
    assert original_rtl(*case)[1] is True
    # Cancellation is visible before arbitration, so it releases the credit.
    cancelled = (2, 1, 1, 0, 1, 0, 0, 1, 0)
    assert reference(*cancelled)[1] is True
    # Missing cancellation/issue means the one-bit guard can starve background
    # indefinitely at free_count=1. This is a required environment contract,
    # not a proven liveness property of the controller.
    state = True
    for _ in range(256):
        _, issued, state = reference(2, state, 1, 0, 1, 0, 0, 0, 0)
        assert not issued and state
    print(f"PASS {checks} independent truth-table checks; {old_failures} old-RTL mismatches")
    print("COUNTEREXAMPLE same-cycle refill blocked after fix; cancellation releases credit")
    print("LIVENESS WARNING: 256-cycle starvation trace without cancel/critical issue")


if __name__ == "__main__":
    run()
