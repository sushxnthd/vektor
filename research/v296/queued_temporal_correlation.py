#!/usr/bin/env python3
"""V296: prospective synthetic Markov-hotspot FIFO falsification.

Not a GPU measurement. Protocol: QUEUED_TEMPORAL_CORRELATION_PREREG_20261025.md.
"""
import argparse
import itertools
import json
import math
import random
from collections import deque

BANKS, SLOTS, DEPTH = 16, 4, 8
P, H = .8, .75
BURN, EVAL, CAL = 10000, 80000, 50000


def stream(cycles, seed, p, h, sticky):
    rng = random.Random(seed)
    hot = rng.randrange(BANKS)
    for _ in range(cycles):
        if rng.random() >= sticky:
            hot = rng.randrange(BANKS)
        row = []
        for _ in range(SLOTS):
            if rng.random() >= p:
                row.append(None)
            elif rng.random() < h:
                row.append(hot)
            else:
                row.append((hot + 1 + rng.randrange(BANKS - 1)) % BANKS)
        yield tuple(row)


def serial_select(heads):
    used = set()
    result = []
    for bank in heads:
        ok = bank is not None and bank not in used
        result.append(ok)
        if ok:
            used.add(bank)
    return tuple(result)


def pairwise_select(heads):
    # Same-bank, two-read-port restriction: pairwise conflicts are sufficient.
    conflict = [[a is not None and a == b for b in heads] for a in heads]
    selected = [False] * len(heads)
    for i, bank in enumerate(heads):
        selected[i] = bank is not None and not any(
            selected[j] and conflict[j][i] for j in range(i))
    return tuple(selected)


def replay(trace, burn=BURN, depth=DEPTH):
    queues = [deque() for _ in range(SLOTS)]
    offered = dropped = admitted = blocked = occupancy = mismatch = 0
    total_offered = total_dropped = total_admitted = 0
    cycles = 0
    for cycle, arrivals in enumerate(trace):
        if len(arrivals) != SLOTS:
            raise ValueError("wrong issue width")
        new = sum(b is not None for b in arrivals)
        lost = 0
        for i, bank in enumerate(arrivals):
            if bank is None:
                continue
            if not 0 <= bank < BANKS:
                raise ValueError("invalid bank")
            if len(queues[i]) == depth:
                lost += 1
            else:
                queues[i].append(bank)
        heads = tuple(q[0] if q else None for q in queues)
        serial = serial_select(heads)
        pairwise = pairwise_select(heads)
        if serial != pairwise:
            mismatch += 1
            raise AssertionError("V296/serial mismatch at cycle %d" % cycle)
        reads = [0] * BANKS
        for i, yes in enumerate(serial):
            if yes:
                reads[heads[i]] += 2
                queues[i].popleft()
        if max(reads) > 2:
            raise AssertionError("read-port violation")
        issued = sum(serial)
        total_offered += new
        total_dropped += lost
        total_admitted += issued
        if cycle >= burn:
            offered += new
            dropped += lost
            admitted += issued
            blocked += sum(h is not None for h in heads) - issued
            occupancy += sum(map(len, queues))
            cycles += 1
    if total_offered != total_dropped + total_admitted + sum(map(len, queues)):
        raise AssertionError("queue conservation")
    if cycles <= 0:
        raise ValueError("no measured cycles")
    return dict(admissions_per_cycle=admitted/cycles,
                offered_per_cycle=offered/cycles,
                dropped_per_cycle=dropped/cycles,
                blocked_per_cycle=blocked/cycles,
                mean_queue_occupancy=occupancy/cycles,
                mismatch_cycles=mismatch,
                queue_conservation=True, measured_cycles=cycles)


def estimate_request_only(arrivals):
    c_equal = c_pairs = d_equal = d_pairs = offered = cycles = 0
    prev = None
    for row in arrivals:
        valid = [b for b in row if b is not None]
        offered += len(valid)
        cycles += 1
        for i in range(len(valid)):
            for j in range(i+1, len(valid)):
                c_pairs += 1
                c_equal += valid[i] == valid[j]
        if prev is not None:
            for a in valid:
                for b in prev:
                    d_pairs += 1
                    d_equal += a == b
        prev = valid
    if not c_pairs or not d_pairs:
        raise ValueError("insufficient pairs")
    c, d = c_equal/c_pairs, d_equal/d_pairs
    if c <= 1/BANKS:
        raise ValueError("hotspot not identifiable")
    h = (1 + math.sqrt(max(0, (BANKS-1)*(BANKS*c-1))))/BANKS
    sticky = min(1, max(0, (d-1/BANKS)/(c-1/BANKS)))
    return dict(p=offered/(cycles*SLOTS), h=min(1,max(1/BANKS,h)),
                sticky=sticky, within_cycle_collision=c,
                adjacent_cycle_collision=d, within_pairs=c_pairs,
                adjacent_pairs=d_pairs, calibration_cycles=cycles)


def exact_no_queue_q(p, h):
    return 1-(1-p*h)**SLOTS + (BANKS-1)*(1-(1-p*(1-h)/(BANKS-1))**SLOTS)


def case(sticky, calibration_seed, evaluation_seed, prediction_seed):
    est = estimate_request_only(stream(CAL, calibration_seed, P, H, sticky))
    # No admission outcomes from calibration enter the prediction.
    predicted = replay(stream(BURN+EVAL, prediction_seed,
                              est["p"], est["h"], est["sticky"]))
    iid = replay(stream(BURN+EVAL, prediction_seed, est["p"], est["h"], 0))
    observed = replay(stream(BURN+EVAL, evaluation_seed, P, H, sticky))
    truth = observed["admissions_per_cycle"]
    error = abs(predicted["admissions_per_cycle"]-truth)
    iid_error = abs(iid["admissions_per_cycle"]-truth)
    return dict(true_sticky=sticky, inferred=est, observed=observed,
                queued_prediction=predicted, iid_queued_baseline=iid,
                no_queue_baseline=exact_no_queue_q(est["p"], est["h"]),
                abs_error=error, iid_baseline_abs_error=iid_error,
                error_reduction=1-error/iid_error if iid_error else None,
                pass_gate=error<=.08 and iid_error>0
                and error<=.5*iid_error and observed["mismatch_cycles"]==0)


def self_test():
    for heads in itertools.product((None,0,1),repeat=SLOTS):
        assert serial_select(heads)==pairwise_select(heads)
    for seed in (11,12,13):
        r = replay(stream(3000,seed,P,H,.9),burn=500)
        assert r["mismatch_cycles"]==0 and r["queue_conservation"]
    assert abs(exact_no_queue_q(.8,.75)-1.758542)<1e-5
    e = estimate_request_only(stream(15000,98765,P,H,.9))
    assert abs(e["p"]-.8)<.02 and abs(e["h"]-.75)<.03
    assert abs(e["sticky"]-.9)<.05
    print("SELF_TEST_PASS: 81 exhaustive head states; 3 queue replays; request-only estimator")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--evaluate",action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    if args.evaluate:
        cases = [case(.35,296350,297350,298350),
                 case(.95,296950,297950,298950)]
        print(json.dumps(dict(evidence="PROSPECTIVE_SYNTHETIC_NOT_GPU",
                              cases=cases,
                              all_gates_pass=all(c["pass_gate"] for c in cases)),
                         indent=2,sort_keys=True))
        if not all(c["pass_gate"] for c in cases):
            raise SystemExit("FROZEN_GATE_FAIL")
    if not args.self_test and not args.evaluate:
        parser.print_help()


if __name__=="__main__":
    main()
