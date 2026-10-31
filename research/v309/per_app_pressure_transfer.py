#!/usr/bin/env python3
"""V309 per-application conditional service-pressure falsification; NOT a GPU simulator."""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import json
from sector_antichain_full_audit import scan as sector_scan
from v100_sass_profile import profile as sass_profile

SHA = 'aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1'
BANDWIDTHS = (F(8), F(32))
ATTENUATIONS = (F(1), F(1, 2), F(1, 4), F(1, 8))
REDUCTION = F(1, 4)
PENALTY = F(1, 20)


def frac(x):
    return f'{x.numerator}/{x.denominator}'


def ipc(i, s, b, a, r, h, p=F(1)):
    if i <= 0 or s <= 0 or b <= 0 or p <= 0 or not 0 <= a <= 1 or not 0 <= r < 1 or h < 0:
        raise ValueError('invalid model parameters')
    issue = p / (1 + h)
    return issue if a == 0 else min(issue, b * i / (32 * a * s * (1-r)))


def time_oracle(i, s, b, a, r, h, p=F(1)):
    if i <= 0 or s <= 0 or b <= 0 or p <= 0 or not 0 <= a <= 1 or not 0 <= r < 1 or h < 0:
        raise ValueError('invalid parameters')
    return F(i) / max(F(i)*(1+h)/p, F(32*s)*a*(1-r)/b)


def gain(i, s, b, a, r=REDUCTION, h=PENALTY):
    return ipc(i,s,b,a,r,h) / ipc(i,s,b,a,F(0),F(0)) - 1


def sign(i,s,b,a,r=REDUCTION,h=PENALTY):
    return 'WIN' if r > 0 and a > 0 and F(32*s)*a > (1+h)*b*i else 'NO_WIN'


def classify(i,lo,hi,b,a,r=REDUCTION,h=PENALTY):
    g0,g1=gain(i,lo,b,a,r,h),gain(i,hi,b,a,r,h)
    if g0>g1: raise AssertionError('nonmonotonic gain')
    for s,g in ((lo,g0),(hi,g1)):
        if (g>0)!=(sign(i,s,b,a,r,h)=='WIN'): raise AssertionError('sign law mismatch')
        if ipc(i,s,b,a,r,h)!=time_oracle(i,s,b,a,r,h): raise AssertionError('time oracle mismatch')
    status='WIN' if g0>0 else 'NO_WIN' if g1<=0 else 'AMBIGUOUS'
    return {'status':status,'gain_interval':[frac(g0),frac(g1)],
            'break_even_attenuation_interval':[frac((1+h)*b*i/F(32*hi)),frac((1+h)*b*i/F(32*lo))]}


def selftest():
    n=0
    for i in (1,7,31):
        for s in (1,5,37):
            for b in (F(1),F(8),F(32)):
                for a in (F(0),F(1,8),F(1,2),F(1)):
                    for r in (F(0),F(1,4),F(3,4)):
                        for h in (F(0),F(1,20),F(1,2)):
                            assert ipc(i,s,b,a,r,h)==time_oracle(i,s,b,a,r,h)
                            assert (gain(i,s,b,a,r,h)>0)==(sign(i,s,b,a,r,h)=='WIN')
                            if r==0: assert gain(i,s,b,a,r,h)<=0
                            n+=1
    for bad in ((1,1,8,-1,F(1,4),0),(1,1,8,1,1,0),(1,1,8,1,0,-1)):
        try: ipc(*bad)
        except ValueError: pass
        else: raise AssertionError('invalid input accepted')
    return {'status':'PASS','independent_time_oracle_cases':n,'analytic_sign_agreement':True,
            'fixed_address_control_never_wins':True}


def run(archive):
    p=sass_profile(archive)
    s=sector_scan(archive)
    if p['archive_sha256']!=SHA or s['archive_sha256']!=SHA:
        raise AssertionError('archive SHA mismatch')
    apps=p['applications']
    sa=s['applications']
    if len(apps)!=11 or set(apps)!=set(sa):
        raise AssertionError('application identities differ')
    if p['global']['active']!=3937565 or (s['global']['new_sector_lower'],s['global']['new_sector_upper'])!=(1586186,1595385):
        raise AssertionError('frozen global counts mismatch')
    if sum(v['active'] for v in apps.values())!=3937565 or sum(v['new_sector_lower'] for v in sa.values())!=1586186 or sum(v['new_sector_upper'] for v in sa.values())!=1595385:
        raise AssertionError('per-application conservation failed')
    cases={}
    for name in sorted(apps):
        i=apps[name]['active']
        lo,hi=sa[name]['new_sector_lower'],sa[name]['new_sector_upper']
        if i<=0 or lo<=0 or lo>hi: raise AssertionError('invalid application counts')
        scenarios={}
        for b in BANDWIDTHS:
            for a in ATTENUATIONS:
                key=f'B{int(b)}_a{frac(a)}'
                scenarios[key]=classify(i,lo,hi,b,a)
                for x in (lo,hi):
                    if gain(i,x,b,a,F(0),F(0))!=0 or gain(i,x,b,a,F(0),PENALTY)>0:
                        raise AssertionError('fixed-address coalescer unexpectedly wins')
        cases[name]={'active_instructions':i,'conditional_sector_interval':[lo,hi],
                     'conditional_bytes_per_instruction':[frac(F(32*lo,i)),frac(F(32*hi,i))],
                     'scenarios':scenarios}
    pooled={}
    contrasts={}
    for b in BANDWIDTHS:
        for a in ATTENUATIONS:
            key=f'B{int(b)}_a{frac(a)}'
            pooled[key]=classify(3937565,1586186,1595385,b,a)
            counts={k:sum(v['scenarios'][key]['status']==k for v in cases.values())
                    for k in ('WIN','NO_WIN','AMBIGUOUS')}
            status=pooled[key]['status']
            contrasts[key]={'pooled':status,'per_app_counts':counts,
                            'pooled_versus_robust_disagreement_count':counts['NO_WIN'] if status=='WIN' else counts['WIN'] if status=='NO_WIN' else None}
    return {'status':'PASS',
            'evidence_tier':'historical_source_conditional_sector_service_model_NOT_GPU_performance',
            'producer_identity_verified':False,'hardware_mechanism_promoted':False,
            'archive_sha256':SHA,'source_conditional_global_sector_interval':[1586186,1595385],
            'targeted_BFS_eight_sector_tightening_excluded':True,
            'parameters':{'hypothetical_reduction':frac(REDUCTION),'issue_penalty':frac(PENALTY),
                          'bandwidth_bytes_per_cycle':[frac(x) for x in BANDWIDTHS],
                          'service_reaching_fraction':[frac(x) for x in ATTENUATIONS]},
            'applications':cases,'pooled':pooled,'contrasts':contrasts,'selftest':selftest(),
            'limitations':['Rodinia already explored, not unseen',
                           'No measured cache miss fraction, GPU cycles, timing or power',
                           'Hypothetical sector reduction has no RTL implementation',
                           'Fixed-address ideal coalescer cannot reduce sector count']}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('archive',nargs='?')
    parser.add_argument('--selftest',action='store_true')
    args=parser.parse_args()
    if args.selftest: print(json.dumps(selftest(),sort_keys=True))
    if args.archive: print(json.dumps(run(args.archive),sort_keys=True,indent=2))
    elif not args.selftest: parser.error('archive required')
