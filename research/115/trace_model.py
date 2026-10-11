"""Vektor-115: post-MMU translation provenance (synthetic host model).

No Vortex runtime trace or GPU-cycle measurement is claimed.
"""
from dataclasses import dataclass
import random

PAGE=4096
LINE=32

@dataclass(frozen=True)
class Req:
    rid: int
    uuid: int
    hart: int
    tag: int
    va: int
    size: int = 4

@dataclass(frozen=True)
class Paired:
    rid: int
    uuid: int
    hart: int
    tag: int
    va: int
    pa: int

def translate(r, pages):
    if r.va < 0 or r.size < 1 or r.va % r.size or (r.va % PAGE)+r.size>PAGE:
        raise ValueError('misaligned or cross-page access')
    return pages[r.va//PAGE]*PAGE+(r.va%PAGE)

def paired_trace(reqs, pages, delivery):
    # Translation is logged where both virtual and physical addresses coexist.
    # The delivery permutation simulates hit-under-miss/replay reordering.
    return [Paired(r.rid,r.uuid,r.hart,r.tag,r.va,translate(r,pages)) for r in delivery]

def naive_fifo(reqs, physical_events):
    """Incorrect: zips ingress VAs to physical egress by (uuid,hart,tag)."""
    pending={}
    for r in reqs:
        pending.setdefault((r.uuid,r.hart,r.tag),[]).append(r)
    out=[]
    for p in physical_events:
        key=(p.uuid,p.hart,p.tag)
        r=pending[key].pop(0)
        out.append(Paired(r.rid,r.uuid,r.hart,r.tag,r.va,p.pa))
    return out

def aggregate_lanes(addrs, line=LINE):
    """Coalescer request granularity, not GPU lane-level trace provenance."""
    return sorted({a//line for a in addrs})

def sample(seed, n, exploratory=False):
    rng=random.Random(seed)
    errors=0
    reorder=0
    reduced=0
    for case in range(n):
        k=rng.randint(2,8)
        # Intentionally repeated uuid/hart/tag to stress ambiguous joins.
        vpn=rng.sample(range(1,1024),k)
        ppn=rng.sample(range(2048,8192),k)
        pages=dict(zip(vpn,ppn))
        reqs=[Req(i,case%7,case%3,case%5,vpn[i]*PAGE+32*(i%4)) for i in range(k)]
        delivery=reqs[:]
        rng.shuffle(delivery)
        reorder+=int(delivery!=reqs)
        truth=paired_trace(reqs,pages,delivery)
        naive=naive_fifo(reqs,truth)
        truth_by_id={p.rid:p.pa for p in truth}
        errors+=sum(p.pa!=truth_by_id[p.rid] for p in naive)
        assert all(p.pa==translate(reqs[p.rid],pages) for p in truth)
        lanes=[rng.randrange(0,8)*4 for _ in range(rng.randint(2,32))]
        reduced+=int(len(aggregate_lanes(lanes))<len(lanes))
    return dict(seed=seed,configurations=n,reordered=reorder,
                naive_misattributed_records=errors,coalesced_cases=reduced,
                paired_misattributed_records=0,experimental_class='SURPRISE' if exploratory else 'DISCRIMINATION')

def main():
    import json
    groups=[sample(115001,256),sample(115002,128),sample(115003,48,True)]
    print(json.dumps(groups,indent=2))
    return groups

if __name__=='__main__': main()
