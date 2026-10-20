# V244 standalone independent truth-table checker. Python 3, no deps.
import itertools
def dut(q,t0,t1,v0,v1):
    a=bool(v0 and q==t0)
    b=bool(v1 and q==t1 and not a)
    return bool(a or b),int(b),int(a),int(b)
def reference(q,tags,valids):
    hits=[i for i in range(2) if valids[i] and tags[i]==q]
    w=hits[0] if hits else None
    return w is not None, w if w is not None else 0, int(w==0),int(w==1)
n=0
for q,t0,t1 in itertools.product(range(16),repeat=3):
    for v0,v1 in itertools.product((0,1),repeat=2):
        assert dut(q,t0,t1,v0,v1)==reference(q,(t0,t1),(v0,v1))
        n+=1
assert n==16384
print('PASS',n)
