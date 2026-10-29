#!/usr/bin/env python3
"""V302: bounded reduction-only atomic combiner, equal-entry controls.
Synthetic execution-time proxy, NOT GPU IPC. Python 3 standard library only.
"""
import argparse
import collections
import json
import random
import statistics

MASK = (1 << 32) - 1


def workload(regime, seed, steps=10000):
    rng = random.Random(seed)
    rate = {'H1': .8, 'H2': .35, 'H3': .75, 'H4': .05, 'H5': .8}[regime]
    hot = [.55, .15, .12, .10, .08]
    programs = []
    for warp in range(4):
        stream = []
        for t in range(steps):
            if rng.random() >= rate:
                stream.append(())
                continue
            if regime in ('H1', 'H3'):
                base = (t // 128) % 2 * 5 if regime == 'H3' else 0
                keys = [base + rng.choices(range(5), hot)[0] for _ in range(4)]
            elif regime == 'H5':
                keys = [rng.choices(range(2), [.8, .2])[0] for _ in range(4)]
            else:
                n = 256 if regime == 'H2' else 32
                keys = [rng.randrange(n) for _ in range(4)]
            # Within-warp aggregation is present in every policy.
            group = collections.Counter(keys)
            stream.append(tuple(group.items()))
        programs.append(stream)
    return programs


def simulate(programs, policy, capacity=4, qlimit=32, age_limit=8):
    assert policy in ('fifo', 'lru', 'lfu')
    steps = len(programs[0]); pointers = [0] * 4
    queue = collections.deque()
    entries = []  # key, sum, count, birth, last, hit
    input_sums = collections.defaultdict(int)
    output_sums = collections.defaultdict(int)
    offered = sum(sum(v for batch in stream for _, v in batch) for stream in programs)
    accepted = serviced = transactions = stalls = maxq = 0
    cycles = 0
    # Each source warp retries its blocked batch. No traffic is dropped.
    while any(p < steps for p in pointers) or queue or entries:
        cycles += 1
        if cycles > 1000000:
            raise AssertionError('nontermination')
        for w in range(4):
            if pointers[w] == steps:
                continue
            batch = programs[w][pointers[w]]
            if len(queue) + len(batch) > qlimit:
                stalls += 1
                continue
            pointers[w] += 1
            for k, v in batch:
                queue.append((k, v))
                input_sums[k] = (input_sums[k] + v) & MASK
                accepted += v
        maxq = max(maxq, len(queue))
        issued = False

        def emit(i):
            nonlocal issued, transactions, serviced
            e = entries.pop(i)
            output_sums[e['key']] = (output_sums[e['key']] + e['sum']) & MASK
            transactions += 1
            serviced += e['count']
            issued = True

        if policy == 'fifo':
            if queue:
                k, v = queue.popleft()
                output_sums[k] = (output_sums[k] + v) & MASK
                transactions += 1
                serviced += v
        else:
            expired = [i for i, e in enumerate(entries) if cycles - e['birth'] >= age_limit]
            if expired:
                emit(min(expired, key=lambda i: entries[i]['birth']))
            for _ in range(4):
                if not queue:
                    break
                k, v = queue[0]
                idx = next((i for i, e in enumerate(entries) if e['key'] == k), None)
                if idx is not None:
                    e = entries[idx]
                    e['sum'] = (e['sum'] + v) & MASK
                    e['count'] += v
                    e['last'] = cycles
                    e['hit'] = min(3, e['hit'] + 1)
                    queue.popleft()
                elif len(entries) < capacity:
                    entries.append(dict(key=k, sum=v, count=v, birth=cycles, last=cycles, hit=0))
                    queue.popleft()
                elif not issued:
                    if policy == 'lfu':
                        victim = min(range(len(entries)), key=lambda i: (entries[i]['hit'], entries[i]['birth']))
                    else:
                        victim = min(range(len(entries)), key=lambda i: entries[i]['last'])
                    emit(victim)
                    entries.append(dict(key=k, sum=v, count=v, birth=cycles, last=cycles, hit=0))
                    queue.popleft()
                else:
                    break
            if not issued and entries and not queue and all(p == steps for p in pointers):
                emit(min(range(len(entries)), key=lambda i: entries[i]['birth']))
    assert accepted == offered == serviced, (accepted, offered, serviced)
    assert dict(input_sums) == dict(output_sums), 'per-key modular conservation failed'
    return dict(cycles=cycles, throughput=serviced / cycles, logical=serviced,
                transactions=transactions, stalls=stalls, max_queue=maxq,
                transaction_reduction=1-transactions/serviced)


def independent_semantics_test():
    # Addition is associative modulo 2^32, and the final state is equal.
    rng = random.Random(301)
    for _ in range(512):
        vals = [rng.randrange(1 << 32) for _ in range(rng.randrange(1, 20))]
        left = sum(vals) & MASK
        rng.shuffle(vals)
        right = 0
        for v in vals:
            right = (right + v) & MASK
        assert left == right
    # A concurrent read makes deferred combining observably wrong.
    original_read = (0 + 1) & MASK
    deferred_read = 0
    assert original_read != deferred_read
    return 512


def run(steps=10000, seeds=range(20261030, 20261038)):
    independent_semantics_test()
    out = {'steps': steps, 'seeds': list(seeds), 'regimes': {}}
    for regime in ('H1', 'H2', 'H3', 'H4', 'H5'):
        samples = {p: [] for p in ('fifo', 'lru', 'lfu')}
        for seed in seeds:
            programs = workload(regime, seed, steps)
            for p in samples:
                samples[p].append(simulate(programs, p))
        means = {p: {k: statistics.mean(s[k] for s in vals) for k in vals[0]} for p, vals in samples.items()}
        out['regimes'][regime] = {'mean': means,
            'lfu_vs_lru': means['lfu']['throughput'] / means['lru']['throughput'],
            'lfu_vs_fifo': means['lfu']['throughput'] / means['fifo']['throughput'],
            'lfu_lru_seed_ratios': [a['throughput']/b['throughput'] for a,b in zip(samples['lfu'],samples['lru'])]}
    h = out['regimes']
    out['gates'] = {'H1_vs_lru':h['H1']['lfu_vs_lru']>=1.05,
                    'H1_vs_fifo':h['H1']['lfu_vs_fifo']>=1.10,
                    'H2_robust':h['H2']['lfu_vs_lru']>=.98,
                    'H3_robust':h['H3']['lfu_vs_lru']>=.95,
                    'H4_robust':h['H4']['lfu_vs_lru']>=.98}
    out['survives'] = all(out['gates'].values())
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--steps', type=int, default=10000)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    seeds = range(100, 102) if args.pilot else range(20261030, 20261038)
    print(json.dumps(run(args.steps if not args.pilot else 300, seeds), indent=2, sort_keys=True))
