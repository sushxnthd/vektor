"""Vektor-053 bounded exhaustive RF admission conservation, stdlib only."""
from itertools import product

def policy_grant(states,banks,slots,ptr,mode,W=2,O=3,B=2,P=2):
    order=[(ptr+k)%W for k in range(W)]
    if mode==2:
        order.sort(key=lambda w:-sum(states[w*O+o]==2 for o in range(O)))
    used=[0]*B; grant=0; count=0; first=None
    for w in order:
        for o in range(O):
            i=w*O+o; b=banks[i]
            if states[i]==1 and count<slots and used[b]<P:
                grant|=1<<i; used[b]+=1; count+=1
                if first is None: first=w
    nxt=(ptr+1)%W if mode==0 else ((first+1)%W if first is not None else ptr)
    return grant,count,nxt

def test():
    checks=0; differing_grants=0
    for states in product(range(3),repeat=6):
        for banks in product(range(2),repeat=6):
            demand=[sum(states[i]==1 and banks[i]==b for i in range(6)) for b in range(2)]
            for slots in range(7):
                expected=min(slots,sum(min(2,n) for n in demand))
                for ptr in range(2):
                    out=[policy_grant(states,banks,slots,ptr,p) for p in range(3)]
                    assert all(n==expected for _,n,_ in out)
                    flipped=tuple(1-b for b in banks)
                    assert all(policy_grant(states,flipped,slots,ptr,p)==out[p] for p in range(3))
                    differing_grants+=len({r[0] for r in out})>1
                    checks+=1
    assert checks==653184 and differing_grants>0
    print("PASS exhaustive configurations",checks,"policy checks",3*checks,
          "grant-set differences",differing_grants)
if __name__=="__main__": test()
