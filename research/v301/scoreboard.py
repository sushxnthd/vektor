"""V301 event-conserving response-scoreboard coalescing micro-model.

Each completion is (warp, epoch, sector-bit).  A merge is legal only for the
same (warp, epoch); epochs cannot be conflated across scoreboard reset.
The input producer backlog is lossless; all runs drain to completion.
"""
from collections import deque, defaultdict
import argparse, json, random, statistics


def stream(seed, cycles, lanes, offered, warps, hot=0., hot_warp=0, epoch_period=1024):
    rng = random.Random(seed)
    events = []
    for t in range(cycles):
        for _ in range(lanes):
            if rng.random() < offered:
                warp = hot_warp if rng.random() < hot else rng.randrange(warps)
                epoch = t // epoch_period
                sector = 1 << rng.randrange(8)
                events.append((t, warp, epoch, sector))
    return events


def merge_batch(batch):
    out = []
    pos = {}
    for t, w, e, mask in batch:
        key = (w, e)
        if key in pos:
            idx = pos[key]
            a, b, c, old = out[idx]
            out[idx] = (a, b, c, old | mask)
        else:
            pos[key] = len(out)
            out.append((t, w, e, mask))
    return out


def run(events, policy, capacity=8, ingress=4, banks=2, return_digest=False):
    assert policy in ('fifo', 'ingress', 'queue_merge', 'banked', 'set2', 'set4')
    q = deque()
    pending = deque()
    received = defaultdict(int)
    emitted = defaultdict(int)
    arrivals = 0
    writes = 0
    peak_pending = 0
    sum_backlog = 0
    latency = []
    t = 0
    i = 0
    last_t = events[-1][0] if events else 0
    while i < len(events) or pending or q or t <= last_t:
        while i < len(events) and events[i][0] == t:
            ev = events[i]
            pending.append(ev)
            received[(ev[1], ev[2])] |= ev[3]
            i += 1
            arrivals += 1
        # One scoreboard RMW port, or one per physical bank for the control.
        if policy == 'banked':
            used = set()
            keep = deque()
            for item in q:
                bank = item[1] % banks
                if bank not in used:
                    used.add(bank)
                    emitted[(item[1], item[2])] |= item[3]
                    writes += 1
                    latency.append(t - item[0])
                else:
                    keep.append(item)
            q = keep
        elif q:
            item = q.popleft()
            emitted[(item[1], item[2])] |= item[3]
            writes += 1
            latency.append(t - item[0])
        # Input admits a prefix, never discards a completion.
        count = 0
        this_cycle_keys = {}
        while pending and count < ingress:
            ev = pending[0]
            key = (ev[1], ev[2])
            if policy in ('queue_merge', 'set2', 'set4'):
                found = next((j for j, old in enumerate(q) if (old[1], old[2]) == key), None)
                if found is not None:
                    old = q[found]
                    q[found] = (min(old[0], ev[0]), old[1], old[2], old[3] | ev[3])
                    pending.popleft()
                    count += 1
                    continue
            if policy == 'ingress' and key in this_cycle_keys:
                found = this_cycle_keys[key]
                old = q[found]
                q[found] = (min(old[0], ev[0]), old[1], old[2], old[3] | ev[3])
                pending.popleft()
                count += 1
                continue
            if policy in ('set2', 'set4'):
                ways = 2 if policy == 'set2' else 4
                assert capacity % ways == 0 and capacity >= ways
                num_sets = capacity // ways
                set_idx = ev[1] % num_sets
                if sum(1 for old in q if old[1] % num_sets == set_idx) >= ways:
                    break
            if len(q) >= capacity:
                break
            q.append(ev)
            if policy == 'ingress':
                this_cycle_keys[key] = len(q)-1
            pending.popleft()
            count += 1
        peak_pending = max(peak_pending, len(pending))
        sum_backlog += len(pending) + len(q)
        t += 1
        if t > 1000000:
            raise RuntimeError('unbounded drain')
    assert received == emitted, (policy, len(received), len(emitted))
    result = {'policy': policy, 'cycles': t, 'arrivals': arrivals, 'writes': writes,
            'event_rate': arrivals / t, 'write_rate': writes / t,
            'mean_backlog': sum_backlog / t, 'peak_pending': peak_pending,
            'mean_oldest_entry_age': statistics.mean(latency) if latency else 0}
    if return_digest:
        result['digest'] = dict(emitted)
    return result


def experiment(seed, cycles=5000, lanes=4, offered=.8, warps=32, hot=0., epoch_period=1024):
    events = stream(seed, cycles, lanes, offered, warps, hot, epoch_period=epoch_period)
    return {p: run(events, p) for p in ('fifo', 'ingress', 'queue_merge', 'banked', 'set2', 'set4')}


def expected_unique(warps, hot, lanes):
    # Conditional on all lanes having events; independent draws with replacement.
    p0 = hot + (1-hot)/warps
    p1 = (1-hot)/warps
    return (1-(1-p0)**lanes) + (warps-1)*(1-(1-p1)**lanes)


def selftest():
    assert len(merge_batch([(0,1,0,1),(0,1,0,2),(0,1,1,4)])) == 2
    assert merge_batch([(0,1,0,1),(0,1,0,2)])[0][-1] == 3
    for s in range(8):
        for w in (1,2,4,16):
            events=stream(s, 70, 4, .8, w, .4)
            for p in ('fifo','ingress','queue_merge','banked','set4'):
                run(events,p,capacity=3)
    print('selftest: 128 lossless policy/configuration runs passed')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--holdout', action='store_true')
    parser.add_argument('--selftest', action='store_true')
    args=parser.parse_args()
    if args.selftest:
        selftest()
        return
    # Pilot seeds are disjoint from frozen future holdouts [101..120].
    if args.holdout:
        cases={'H1_predicted_win':(.60,48,.55,1024),
               'H2_predicted_no_win':(.90,256,0.,1024),
               'H3_low_load':(.20,32,.5,1024),
               'H4_hot_set2_tie':(.95,16,.9,1024),
               'H5_fast_epoch':(.60,48,.55,16)}
    else:
        cases={'hot_high':(.9,16,.9,1024),'uniform_high':(.9,256,0.,1024),
               'hot_low':(.15,16,.9,1024),'medium':(.55,32,.5,1024)}
    seeds=range(101,121) if args.holdout else range(4)
    output={}
    for name,(offered,warps,hot,epoch_period) in cases.items():
        results=[experiment(s, offered=offered,warps=warps,hot=hot,epoch_period=epoch_period) for s in seeds]
        output[name]={'settings':{'offered':offered,'warps':warps,'hot':hot,'epoch_period':epoch_period},
            'avg':{p:{k:round(statistics.mean(r[p][k] for r in results),6)
                      for k in ('cycles','event_rate','mean_backlog','peak_pending','mean_oldest_entry_age','writes')}
                   for p in results[0]},
            'expected_unique_full_batch':round(expected_unique(warps,hot,4),6)}
    print(json.dumps(output,indent=2,sort_keys=True))

if __name__=='__main__':
    main()
