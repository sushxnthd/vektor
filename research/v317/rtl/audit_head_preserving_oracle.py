#!/usr/bin/env python3
"""Independent age-head oracle audit; does not import primary evaluator."""
import itertools, json, random, sys

def check(q,cap=4):
    # Recursive search over include/skip decisions, with independent in-place port counts.
    n=max(max(a,b) for a,b in q)+1
    usage=[0]*n
    def optimum(i,force_head):
        if i==4: return 0
        a,b=q[i]
        best=-100 if (i==0 and force_head) else optimum(i+1,force_head)
        if usage[a]+(2 if a==b else 1)<=2 and (a==b or usage[b]+1<=2):
            usage[a]+=1; usage[b]+=1
            best=max(best,1+optimum(i+1,force_head))
            usage[a]-=1; usage[b]-=1
        return best
    greedy_usage=[0]*n; g=0
    for a,b in q:
        if greedy_usage[a]+(2 if a==b else 1)>2 or (a!=b and greedy_usage[b]+1>2): continue
        greedy_usage[a]+=1;greedy_usage[b]+=1;g+=1
    h=optimum(0,True);u=optimum(0,False)
    assert g<=h<=u and 1<=g<=4
    return min(g,cap),min(h,cap),min(u,cap)

def audit(path):
    r=json.load(open(path))
    assert r['seeds']==[4127,6151,8111] and r['batches_per_seed']==10000
    assert check([(0,1),(0,0),(1,1),(2,2)])==(2,2,3)
    assert check([(0,0),(1,1),(2,2),(3,3)])==(4,4,4)
    exact={}
    for B in (2,4):
        total=[0,0,0]; bypass=improve=0;count=0
        for x in itertools.product(range(B),repeat=8):
            g,h,u=check(list(zip(x[::2],x[1::2])))
            total[0]+=g;total[1]+=h;total[2]+=u
            bypass+=int(u>h);improve+=int(h>g);count+=1
        ref=r['exhaustive']['B'+str(B)]
        assert count==ref['batches']
        assert total==[ref['greedy_grants'],ref['head_preserving_grants'],ref['unrestricted_grants']]
        assert abs(improve/count-ref['head_gain_probability'])<1e-12
        assert abs(bypass/count-ref['unrestricted_head_bypass_probability'])<1e-12
        exact['B'+str(B)]=dict(batches=count,greedy=total[0],head=total[1],unrestricted=total[2])
    configs=[('uniform16',16,'uniform',4),('uniform4',4,'uniform',4),('hot65_16',16,'hot65',4),('hot65_16_cap2',16,'hot65',2),('samebank70_16',16,'samebank70',4)]
    held={}
    for j,(name,B,kind,cap) in enumerate(configs):
        ref=r['regimes'][name]
        assert ref['batches']==30000
        assert 0<=ref['greedy_grants']<=ref['head_preserving_grants']<=ref['unrestricted_grants']<=4*30000
        assert abs(ref['head_over_greedy']-ref['head_preserving_grants']/ref['greedy_grants'])<1e-12
        assert abs(ref['unrestricted_over_greedy']-ref['unrestricted_grants']/ref['greedy_grants'])<1e-12
        assert abs(ref['exact_head_gain_identity']-ref['head_over_greedy'])<1e-12
        rng=random.Random(900719+j)
        total=[0,0,0]
        for _ in range(2000):
            def bank():
                if kind=='hot65':return 0 if rng.random()<.65 else rng.randrange(1,B)
                return rng.randrange(B)
            q=[]
            for i in range(4):
                a=bank();b=a if kind=='samebank70' and rng.random()<.70 else bank()
                q.append((a,b))
            v=check(q,cap)
            for k in range(3):total[k]+=v[k]
        ratio=total[1]/total[0]
        # Independent seeds: broad tolerance only; not replayed Monte Carlo.
        assert abs(ratio-ref['head_over_greedy'])<.015,(name,ratio,ref['head_over_greedy'])
        held[name]=dict(samples=2000,greedy=total[0],head=total[1],unrestricted=total[2],head_ratio=ratio)
    return dict(decision='PASS independent exhaustive and separately seeded holdouts; not physical signoff',exhaustive=exact,holdouts=held)
if __name__=='__main__':print(json.dumps(audit(sys.argv[1]),indent=2,sort_keys=True))
