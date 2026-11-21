"""Independent finite-horizon FIFO/bank service falsification (synthetic only).

Each request is (bank, release_cycle). One output per cycle, one port per bank.
For a single issue slot, bank identity cannot constrain a cycle beyond release;
this checker explicitly tests that invariance and does not mislabel the result
as a bank-conflict experiment. Compare FIFO heads to reorderable queues.
"""
from functools import lru_cache
from itertools import product


def optimal_completion(queues, horizon, preserve_order=True, output_slots=1, bank_ports=1):
    queues = tuple(tuple(q) for q in queues)
    assert horizon >= 0 and output_slots >= 1 and bank_ports >= 1

    @lru_cache(None)
    def solve(t, remaining):
        if t == horizon:
            return 0
        candidates = []
        for source, q in enumerate(remaining):
            for index in ((0,) if preserve_order else range(len(q))):
                if index < len(q) and q[index][1] <= t:
                    candidates.append((source, index, q[index][0]))
        best = solve(t + 1, remaining)

        def enumerate_choices(start, chosen, counts):
            nonlocal best
            if chosen:
                next_state = list(remaining)
                for source, index, _ in sorted(chosen, reverse=True):
                    q = next_state[source]
                    next_state[source] = q[:index] + q[index + 1:]
                best = max(best, len(chosen) + solve(t + 1, tuple(next_state)))
            if len(chosen) == output_slots:
                return
            used_sources = {s for s, _, _ in chosen}
            for k in range(start, len(candidates)):
                s, i, bank = candidates[k]
                if s in used_sources or counts.get(bank, 0) >= bank_ports:
                    continue
                counts[bank] = counts.get(bank, 0) + 1
                enumerate_choices(k + 1, chosen + [(s, i, bank)], counts)
                counts[bank] -= 1
        enumerate_choices(0, [], {})
        return best
    return solve(0, queues)


def audit():
    hol = (((0, 2), (1, 0)),)
    assert (optimal_completion(hol, 2), optimal_completion(hol, 2, False)) == (0, 1)
    # Simultaneous bank collision matters only with >1 output slot.
    collision = (((0, 0),), ((0, 0),))
    assert optimal_completion(collision, 1, output_slots=2) == 1
    assert optimal_completion(collision, 1, output_slots=2, bank_ports=2) == 2
    cases = loose = 0
    for releases in product(range(3), repeat=4):
        for banks in product(range(2), repeat=4):
            qs = (tuple(zip(banks[:2], releases[:2])), tuple(zip(banks[2:], releases[2:])))
            ordered = optimal_completion(qs, 3)
            relaxed = optimal_completion(qs, 3, False)
            assert ordered <= relaxed
            # At one issue per cycle, bank labels cannot change either optimum.
            relabelled = tuple(tuple((0, release) for _, release in q) for q in qs)
            assert ordered == optimal_completion(relabelled, 3)
            assert relaxed == optimal_completion(relabelled, 3, False)
            cases += 1
            loose += ordered < relaxed
    assert (cases, loose) == (1296, 432)
    return {"cases": cases, "strictly_loose": loose, "single_slot_bank_invariant": True,
            "two_slot_collision_service": 1, "two_port_collision_service": 2}


if __name__ == '__main__':
    print(audit())
