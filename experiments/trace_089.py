"""Deterministic Vektor-089 trace for independent C++17 event replication."""
from cancel_aba_089 import TagMachine
from pathlib import Path
import random
out=['cycle,bits,bound,policy,offer,cancel,delay,bad,correct,stale,stall,admitted,canceled,idle,violations']
for bits,bound,seed in ((1,3,200),(2,6,201),(3,9,202),(4,6,203)):
    rng=random.Random(seed)
    models=[TagMachine(bits,bound,p) for p in ('unsafe','quarantine','oracle','quarantine_boundary')]
    for t in range(4096):
        offer=int(rng.random()<.95)
        cancel=int(rng.random()<.45)
        delay=rng.randint(1,bound)
        for p,m in enumerate(models):
            m.step(offer,cancel,delay)
            d=m.metrics()
            out.append(','.join(map(str,[t,bits,bound,p,offer,cancel,delay,d['false_accept'],d['correct'],d['stale_rejected'],d['tag_stalls'],d['admitted'],d['canceled'],d['idle'],d['violations']])))
Path(__file__).with_name('trace_089.csv').write_text('\n'.join(out)+'\n')
print('trace rows',len(out)-1)
