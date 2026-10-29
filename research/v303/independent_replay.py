"""Independent event-loop replay for the three frozen V303 kernels.

Deliberately does not import sim.vektor.pipeline. It is a second implementation
of issue, RF-bank, LRU and dependency accounting to cross-check the main model.
"""
from collections import OrderedDict


def kernel(name):
    waves = []
    for w in range(32):
        seq = []
        if name == "H1":
            seq = [("fp32", (0, 1), 2 + i % 30, 4) for i in range(64)]
        elif name == "H2":
            reg = 2
            for _ in range(64):
                dst = 3 if reg == 2 else 2
                seq.append(("fp32", (reg, 1), dst, 4))
                reg = dst
        elif name == "H3":
            for i in range(8):
                loaded = 2 + i % 8
                seq.extend([
                    ("load", (), loaded, 120),
                    ("fp32", (loaded, 1), 10 + i % 8, 4),
                ])
        else:
            raise ValueError(name)
        waves.append(seq)
    return waves


def run(name, capacity, policy):
    if policy not in ("invalidate", "ideal_update"):
        raise ValueError(policy)
    waves = kernel(name)
    pc = [0] * 32
    ready = [{} for _ in range(32)]
    cache = OrderedDict()
    rr = 0
    cycle = 0
    rf = hits = bank_stalls = issued_total = 0
    outstanding = []
    while any(pc[w] < len(waves[w]) for w in range(32)):
        cycle += 1
        outstanding = [t for t in outstanding if t > cycle]
        issued = 0
        bank_reads = {}
        next_rr = rr
        memused = 0
        for off in range(32):
            if issued >= 4:
                break
            w = (rr + off) % 32
            if pc[w] >= len(waves[w]):
                continue
            op, src, dst, latency = waves[w][pc[w]]
            if any(ready[w].get(r, 0) > cycle for r in src):
                continue
            if op == "load" and (memused >= 2 or len(outstanding) >= 64):
                continue
            required = {}
            for r in src:
                if (w, r) in cache:
                    continue
                bank = r % 16
                required[bank] = required.get(bank, 0) + 1
            if any(bank_reads.get(b, 0) + n > 2 for b, n in required.items()):
                bank_stalls += 1
                continue
            for r in src:
                key = (w, r)
                if key in cache:
                    hits += 1
                    cache.move_to_end(key)
                else:
                    rf += 1
                    bank = r % 16
                    bank_reads[bank] = bank_reads.get(bank, 0) + 1
                    if capacity:
                        cache[key] = None
                        if len(cache) > capacity:
                            cache.popitem(last=False)
            issued += 1
            issued_total += 1
            next_rr = (w + 1) % 32
            if op == "load":
                memused += 1
                outstanding.append(cycle + 120)
            if dst is not None:
                if policy == "invalidate":
                    cache.pop((w, dst), None)
                ready[w][dst] = cycle + latency
            pc[w] += 1
        rr = next_rr
        if cycle > 100000:
            raise RuntimeError("independent replay exceeded limit")
    return {
        "cycles": cycle,
        "rf_reads": rf,
        "operand_cache_hits": hits,
        "bank_stalls": bank_stalls,
        "issue_utilization": issued_total / (4 * cycle),
    }
