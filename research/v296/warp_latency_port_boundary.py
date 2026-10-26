#!/usr/bin/env python3
"""V296 synthetic warp-scoreboard latency/port falsification.

One outstanding operation per warp; each op reads two RF banks (two ports
per bank), and completes after L cycles. This is NOT a GPU trace, a GPU
performance measurement, or a physical clock. V296 and serial share exact
issue semantics; only the symmetric operand-capture latency differs.
"""
import argparse
import json
import random

BANKS, PORTS, ISSUE = 16, 2, 4
BURN, MEASURE, OPS_PER_WARP = 2000, 18000, 25000


def traces(warps, seed, hotspot):
    rng = random.Random(seed)
    # Generate all requests before replay. Both implementations see identical
    # per-warp sequences; no outcomes are used to generate their bank choices.
    out = []
    for _ in range(warps):
        seq = []
        for _ in range(OPS_PER_WARP):
            if rng.random() < hotspot:
                a = 0
            else:
                a = rng.randrange(BANKS)
            b = a if rng.random() < 0.2 else rng.randrange(BANKS)
            seq.append((a, b))
        out.append(seq)
    return out


def fits(used, a, b):
    return used[a] + (2 if a == b else 1) <= PORTS and (a == b or used[b] < PORTS)


def simulate(requests, latency, cycles=BURN + MEASURE, burn=BURN):
    if not isinstance(latency, int) or isinstance(latency, bool) or latency < 1:
        raise ValueError('latency must be positive integer')
    warps = len(requests)
    if warps < 1 or not 0 <= burn < cycles or any(len(seq) < cycles for seq in requests):
        raise ValueError('insufficient per-warp requests')
    # An op issued at t releases its warp at t+latency, before issue.
    next_ready = [0] * warps
    ptr = [0] * warps
    cursor = 0
    issued = [0] * cycles
    eligible = [0] * cycles
    bank_reject = [0] * cycles
    for tick in range(cycles):
        used = [0] * BANKS
        selected = 0
        rejects = 0
        elig = sum(tick >= t for t in next_ready)
        for off in range(warps):
            w = (cursor + off) % warps
            if tick < next_ready[w]:
                continue
            a, b = requests[w][ptr[w]]
            if not fits(used, a, b):
                rejects += 1
                continue
            used[a] += 1
            used[b] += 1
            ptr[w] += 1
            next_ready[w] = tick + latency
            selected += 1
            if selected == ISSUE:
                break
        cursor = (cursor + 1) % warps
        issued[tick] = selected
        eligible[tick] = elig
        bank_reject[tick] = rejects
        if max(used) > PORTS:
            raise AssertionError('RF read-port violation')
    n = cycles - burn
    return {'ops_per_cycle': sum(issued[burn:]) / n,
            'eligible_per_cycle': sum(eligible[burn:]) / n,
            'bank_rejections_per_cycle': sum(bank_reject[burn:]) / n,
            'issue_histogram': [issued[burn:].count(i) for i in range(ISSUE + 1)],
            'issued_total': sum(issued[burn:]),
            'measured_cycles': n, 'latency': latency}


def independent_reference(requests, latency, cycles):
    """Different event-list implementation; compare counts, not formula."""
    warps = len(requests)
    blocked = set()
    release = {}
    pc = [0] * warps
    total = 0
    histogram = [0] * (ISSUE + 1)
    for t in range(cycles):
        for w in release.pop(t, []):
            blocked.remove(w)
        admitted = []
        for k in range(warps):
            w = (t % warps + k) % warps
            if w in blocked:
                continue
            a, b = requests[w][pc[w]]
            bank_reads = [v for selected in admitted for v in requests[selected][pc[selected]]]
            if bank_reads.count(a) + 1 + (a == b) > PORTS:
                continue
            if a != b and bank_reads.count(b) + 1 > PORTS:
                continue
            admitted.append(w)
            if len(admitted) == ISSUE:
                break
        for w in admitted:
            blocked.add(w)
            release.setdefault(t + latency, []).append(w)
            pc[w] += 1
        total += len(admitted)
        histogram[len(admitted)] += 1
    return total, histogram


def optimistic_occupancy_bound(warps, latency):
    # Necessary, not sufficient: each warp issues <=1/L; issue width <=4.
    return min(ISSUE, warps / latency)


def case(warps, hotspot, seed, clock_ratio=1.0):
    if not 0 <= hotspot <= 1 or not 0 < clock_ratio <= 4:
        raise ValueError('invalid hotspot or hypothetical clock ratio')
    req = traces(warps, seed, hotspot)
    base = simulate(req, 1)
    retimed = simulate(req, 2)
    a, b = base['ops_per_cycle'], retimed['ops_per_cycle']
    if a <= 0 or b <= 0:
        raise AssertionError('invalid throughput')
    return {'warps': warps, 'hotspot': hotspot, 'seed': seed,
            'serial': base, 'retimed': retimed,
            'equal_clock_gain': b/a - 1,
            'minimum_hypothetical_clock_ratio_for_win': a/b,
            'optimistic_occupancy_ceiling_serial': optimistic_occupancy_bound(warps, 1),
            'optimistic_occupancy_ceiling_retimed': optimistic_occupancy_bound(warps, 2),
            'hypothetical_clock_ratio': clock_ratio,
            'hypothetical_compute_gain': clock_ratio*b/a - 1,
            'same_bank_ports': True, 'same_issue_width': True,
            'evidence_tier': 'SYNTHETIC_WARP_SCOREBOARD_NOT_GPU'}


def self_test():
    assert optimistic_occupancy_bound(2, 2) == 1
    assert optimistic_occupancy_bound(8, 2) == 4
    assert fits([0]*BANKS, 0, 0)
    u = [0]*BANKS
    u[0] = 1
    assert not fits(u, 0, 0)
    req = [[(0, 1)] * 30000 for _ in range(2)]
    for w in (1, 2):
        for l in (1, 2):
            r = simulate(req[:w], l)
            assert abs(r['ops_per_cycle'] - min(w/l, 2)) < 1e-12, (w,l,r)
    for w, h, seed in [(3,0,11),(5,.5,12),(7,.9,13)]:
        req = traces(w, seed, h)
        for l in (1,2,3):
            got = simulate(req,l,cycles=300,burn=0)
            total, hist = independent_reference(req,l,300)
            assert got["issued_total"] == total
            assert got["issue_histogram"] == hist
    # No universal monotonicity theorem under conflict-induced reordering.
    for w, h, seed in [(2,0,11),(4,.5,12),(8,.9,13),(16,.3,14)]:
        r = case(w,h,seed)
        assert r['serial']['ops_per_cycle'] <= r['optimistic_occupancy_ceiling_serial'] + 1e-9
        assert r['retimed']['ops_per_cycle'] <= r['optimistic_occupancy_ceiling_retimed'] + 1e-9
    for bad in (0,-1,1.5,True):
        try: simulate([[(0,1)]*30000],bad)
        except ValueError: pass
        else: raise AssertionError('invalid latency accepted')
    print('WARP_SCOREBOARD_LATENCY_PORT_SELFTEST_PASS')


def evaluate():
    # Frozen in protocol commit 62dd5e2c; synthetic unseen seeds, not GPU.
    cells = [(2,0.0,91371),(4,0.0,91372),(8,0.0,91371),
             (16,0.0,91372),(32,0.0,91371),(8,0.8,91372),
             (16,0.8,91371),(32,0.8,91372)]
    return {'protocol': 'WARP_SCOREBOARD_LATENCY_PORT_PREREG_20261026.md',
            'cases': [case(*x) for x in cells],
            'interpretation': 'SYNTHETIC_SCOREBOARD_FALSIFICATION_ONLY',
            'physical_closure': 'NOT_ESTABLISHED',
            'real_gpu_holdouts': 'UNOPENED'}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--self-test', action='store_true')
    p.add_argument('--evaluate', action='store_true')
    args = p.parse_args()
    if args.self_test: self_test()
    if args.evaluate: print(json.dumps(evaluate(), indent=2, sort_keys=True))
    if not (args.self_test or args.evaluate): p.error('choose --self-test or --evaluate')
