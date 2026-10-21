"""V266 frozen workload generator. Saved before evaluation. Seeds frozen in protocol."""
import random
SEEDS={'positive':266101,'negative':266102,'divergent':266103}
def generate(kind):
    rng=random.Random(SEEDS[kind])
    if kind=='positive':
        phases=[]
        for _ in range(20):
            omissions=list(range(5));rng.shuffle(omissions)
            phases.extend([(tuple(x for x in range(5) if x!=omit),128) for omit in omissions])
        return phases
    if kind=='negative':
        phases=[]
        for _ in range(100):
            words=list(range(4));rng.shuffle(words)
            phases.append((tuple(words),128))
        return phases
    if kind=='divergent':
        return [(tuple(x for x in range(5) if x!=rng.randrange(5)),rng.choice((1,2))) for _ in range(100)]
    raise ValueError(kind)
