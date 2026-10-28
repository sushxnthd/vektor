#!/usr/bin/env python3
"""V296 post-hoc routed-clock/latency sensitivity, not GPU performance evidence.
Source: Actions 40646515864, source commit 84245c21f485c191aea7d352652c0ef036d6d047.
"""
import itertools, json, random, sys
from collections import defaultdict
from decimal import Decimal, getcontext
getcontext().prec=32
T=Decimal('3500'); G=Decimal('50')
S={'D4':Decimal('66.661'),'D8':Decimal('59.643')}
A={'D4':Decimal('19543.01964701699'),'D8':Decimal('26723.956381147218')}

def exact(n,b,l,q):
    states=list(itertools.product(range(l),repeat=n)); ix={s:i for i,s in enumerate(states)}
    rows=[]
    for s in states:
        ready=[i for i,x in enumerate(s) if x==0]; tr=defaultdict(float); reward=0.
        for bits in range(1<<len(ready)):
            chosen=[ready[i] for i in range(len(ready)) if bits>>i&1]
            p=q**len(chosen)*(1-q)**(len(ready)-len(chosen)); granted=set(chosen[:b])
            nxt=tuple(l-1 if i in granted else max(0,x-1) for i,x in enumerate(s))
            tr[ix[nxt]]+=p; reward+=p*len(granted)
        assert abs(sum(tr.values())-1)<1e-12
        rows.append((tr,reward))
    pi=[0.]*len(states); pi[ix[(0,)*n]]=1.
    for _ in range(30000):
        nxt=[0.]*len(states)
        for i,(tr,_) in enumerate(rows):
            for j,p in tr.items(): nxt[j]+=pi[i]*p
        err=sum(abs(a-b) for a,b in zip(pi,nxt)); pi=nxt
        if err<1e-14: break
    else: raise RuntimeError('Markov convergence failure')
    return sum(pi[i]*r for i,(_,r) in enumerate(rows))

def independent_mc(n,b,l,q,seed,cycles=160000):
    rng=random.Random(seed); next_ready=[0]*n; grants=0
    for cycle in range(cycles):
        eligible=[i for i in range(n) if cycle>=next_ready[i] and rng.random()<q]
        for i in eligible[:b]: grants+=1; next_ready[i]=cycle+l
    return grants/cycles

def evaluate():
    physical={}
    for d,s in S.items():
        h=s-G; r=T/(T-h)
        physical[d]={'slack_ps':str(s),'guard_headroom_ps':str(h),
          'fixed_path_min_period_ps':str(T-h),'max_clock_ratio':str(r),
          'max_clock_uplift_pct':str((r-1)*100),'routed_area_um2':str(A[d]),
          'candidate_slices_at_30000':int(Decimal('30000')//A[d]),
          'extra_path_delay_stress_pass_ps':{str(x):h>=x for x in (0,5,10,15,20)}}
    regimes=[]
    for name,n,b,q in [('scarce',2,2,.9),('bandwidth_saturated',4,1,.9),
                        ('balanced',4,2,.55),('sparse',4,2,.2)]:
        t1=exact(n,b,1,q); t2=exact(n,b,2,q)
        mc1=independent_mc(n,b,1,q,17); mc2=independent_mc(n,b,2,q,19)
        assert max(abs(t1-mc1),abs(t2-mc2))<.012
        row={'name':name,'N':n,'B':b,'q':q,'T_L1':t1,'T_L2':t2,
             'independent_mc_L1':mc1,'independent_mc_L2':mc2,
             'required_frequency_ratio':t1/t2}
        for d in physical:
            r=float(physical[d]['max_clock_ratio'])
            row[d+'_best_case_work_ratio']=r*t2/t1
        regimes.append(row)
    return {'source_run':40646515864,'evidence':'post-hoc fixed-path analytical sensitivity',
      'physical':physical,'regimes':regimes,'D4_serial':'setup_and_hold_fail',
      'D8_serial':'censored_timeout','matched_win':False,'gpu_performance':False,
      'assumptions':'3500 ps period, +50 ps setup guard, unchanged path/RC; synthetic independent Bernoulli readiness; hypothetical L1 reference',
      'holdouts':'sealed'}

def selftest():
    for q in (.2,.55,.9):
        assert abs(exact(2,2,1,q)-2*q)<1e-11
        assert abs(exact(2,2,2,q)-2*q/(1+q))<1e-11
    r=evaluate(); assert r['physical']['D8']['extra_path_delay_stress_pass_ps']['10'] is False
    assert r['physical']['D4']['extra_path_delay_stress_pass_ps']['10'] is True
    assert abs(r['regimes'][0]['required_frequency_ratio']-1.9)<1e-10
    assert all(v['candidate_slices_at_30000']==1 for v in r['physical'].values())
    print('V296_ROUTED_CLOCK_CEILING_SELFTEST_PASS')
if __name__=='__main__':
    if '--self-test' in sys.argv: selftest()
    else: print(json.dumps(evaluate(),indent=2,sort_keys=True))
