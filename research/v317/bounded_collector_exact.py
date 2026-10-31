"""Exact bounded-collector service scheduler for tiny synthetic bank workloads.

This is not a GPU simulator, physical bank mapping, or an implemented read-elimination
mechanism. All instructions are initially ready. Candidate AB->A is hypothetical.
"""
from __future__ import annotations
from collections import deque
from itertools import product
from math import ceil

BANKS = "ABC"
CLASSES = ("AB", "BC", "CA")
BASE = (0b011, 0b110, 0b101)
CANDIDATE = (0b001, 0b110, 0b101)


def transitions(state, masks, k, issue=2):
    waiting, active = state
    free = k - len(active)
    for admits in product(*(range(min(n, free) + 1) for n in waiting)):
        if sum(admits) > free:
            continue
        all_active = list(active)
        for typ, n in enumerate(admits):
            all_active.extend([(typ, masks[typ])] * n)
        all_active.sort()
        if not all_active:
            continue
        choices = []
        for bank in range(3):
            choices.append((-1,) + tuple(i for i, (_, mask) in enumerate(all_active)
                                          if mask & (1 << bank)))
        for reads in product(*choices):
            if all(i == -1 for i in reads):
                continue
            remaining = [mask for _, mask in all_active]
            for bank, idx in enumerate(reads):
                if idx != -1:
                    remaining[idx] &= ~(1 << bank)
            if sum(m == 0 for m in remaining) > issue:
                continue
            nxt = (tuple(n-a for n, a in zip(waiting, admits)),
                   tuple(sorted((typ, rem) for (typ, _), rem
                                in zip(all_active, remaining) if rem)))
            yield nxt, (admits, reads)


def solve(counts, k, candidate=False, issue=2, max_states=500000):
    if k < 1 or issue < 1 or any(n < 0 for n in counts):
        raise ValueError("invalid inputs")
    if sum(counts) == 0:
        return 0, []
    masks = CANDIDATE if candidate else BASE
    start, goal = (tuple(counts), ()), ((0, 0, 0), ())
    q, parent = deque([start]), {start: None}
    while q:
        s = q.popleft()
        if s == goal:
            break
        for nxt, action in transitions(s, masks, k, issue):
            if nxt not in parent:
                parent[nxt] = (s, action)
                if len(parent) > max_states:
                    raise RuntimeError("state cap")
                q.append(nxt)
    else:
        raise RuntimeError("no feasible schedule")
    path, node = [], goal
    while node != start:
        prev, action = parent[node]
        path.append(action)
        node = prev
    path.reverse()
    return len(path), path


def independent_validate(counts, k, candidate, path, issue=2):
    """Replay labeled admissions and reads without calling the solver transition."""
    masks = CANDIDATE if candidate else BASE
    next_id = [0, 0, 0]
    admitted, completed, seen_reads = {}, set(), set()
    for admit, reads in path:
        if len(admit) != 3 or any(n < 0 for n in admit):
            raise AssertionError("bad admission")
        for typ, n in enumerate(admit):
            for _ in range(n):
                ident = (typ, next_id[typ])
                next_id[typ] += 1
                admitted[ident] = masks[typ]
        if len(admitted) > k:
            raise AssertionError("collector overflow")
        ordered = sorted(admitted, key=lambda i: (i[0], admitted[i], i[1]))
        if len(reads) != 3 or all(i == -1 for i in reads):
            raise AssertionError("invalid read vector")
        for bank, idx in enumerate(reads):
            if idx == -1:
                continue
            if idx < 0 or idx >= len(ordered):
                raise AssertionError("bad read index")
            ident = ordered[idx]
            if not admitted[ident] & (1 << bank):
                raise AssertionError("duplicate/unrequested read")
            if (ident, bank) in seen_reads:
                raise AssertionError("duplicate physical read")
            seen_reads.add((ident, bank))
            admitted[ident] &= ~(1 << bank)
        done = [ident for ident, mask in admitted.items() if mask == 0]
        if len(done) > issue:
            raise AssertionError("completion width exceeded")
        for ident in done:
            completed.add(ident)
            del admitted[ident]
    if next_id != list(counts) or admitted or len(completed) != sum(counts):
        raise AssertionError("unfinished/missing instructions")
    return True


def independent_reachable(counts, k, candidate, depth, issue=2):
    """Separate bounded-depth state enumerator; never calls solve/transitions."""
    masks = CANDIDATE if candidate else BASE
    frontier = {(tuple(counts), ())}
    for _ in range(depth):
        nxt = set()
        for waiting, active in frontier:
            free = k - len(active)
            for admits in product(*(range(min(n, free) + 1) for n in waiting)):
                if sum(admits) > free:
                    continue
                all_act = list(active) + [(i, masks[i])
                                          for i, n in enumerate(admits)
                                          for _ in range(n)]
                if not all_act:
                    continue
                choices = [(-1,) + tuple(j for j, (_, mask) in enumerate(all_act)
                                         if mask & (1 << b)) for b in range(3)]
                for selected in product(*choices):
                    if selected == (-1, -1, -1):
                        continue
                    updated = list(all_act)
                    for b, j in enumerate(selected):
                        if j != -1:
                            t, mask = updated[j]
                            updated[j] = (t, mask & ~(1 << b))
                    if sum(mask == 0 for _, mask in updated) > issue:
                        continue
                    rem = tuple(sorted((t, mask) for t, mask in updated if mask))
                    waiting2 = tuple(w-a for w, a in zip(waiting, admits))
                    nxt.add((waiting2, rem))
        frontier = nxt
        if ((0, 0, 0), ()) in frontier:
            return True
    return False


def lower_bound(counts, candidate=False, issue=2):
    masks = CANDIDATE if candidate else BASE
    return max([ceil(sum(counts) / issue)] +
               [sum(n for n, m in zip(counts, masks) if m & (1 << b))
                for b in range(3)])
