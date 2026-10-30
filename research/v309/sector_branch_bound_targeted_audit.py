#!/usr/bin/env python3
"""V309 prospective targeted alternative solver on the single antichain-capped row.

Replays the unchanged original full-corpus audit; intercepts only the row that
returned UNKNOWN, then independently attempts a bounded exact branch-and-bound.
Original evidence is conserved. Conditional on an unverified tracer producer.
"""
import argparse
import hashlib
import json
import sector_antichain_full_audit as original
from sector_antichain_dp import exact_sector_extrema as unchanged_dp
from sector_branch_bound import exact_branch_bound, selftest
from format0_sector_envelope import format0_envelope

MAX_NODES=1000000


def scan(archive):
    cases=[]
    def capture(mask,width,tokens,**kwargs):
        prior=unchanged_dp(mask,width,tokens,**kwargs)
        if prior[2]['status'] not in ('state_cap','transition_cap'):
            return prior
        conservative=format0_envelope(mask,width,tokens,0)
        if conservative[4]!='conservative':
            raise AssertionError('unexpected original envelope method')
        lo,hi,meta=exact_branch_bound(mask,width,tokens,node_cap=MAX_NODES)
        old_lo,old_hi=conservative[:2]
        if meta['status']=='exact' and not (old_lo<=lo<=hi<=old_hi):
            raise AssertionError('new solver outside conservative envelope')
        cases.append({
            'visible_mask':hex(mask),'width_bytes':width,'address_tokens':len(tokens),
            'tokens_sha256':hashlib.sha256(' '.join(str(x) for x in tokens).encode()).hexdigest(),
            'prior_status':prior[2]['status'], 'prior_transitions':prior[2]['transitions'],
            'old_interval':[old_lo,old_hi], 'alternative_interval':[lo,hi],
            'alternative':meta,
        })
        return prior  # Do not alter baseline scan or previous counts.
    original.exact_sector_extrema=capture
    result=original.scan(archive)
    g=result['global']
    if (g['new_sector_lower'],g['new_sector_upper'])!=(1586186,1595385):
        raise AssertionError('prior hosted full-corpus result not reproduced')
    if g.get('dp_state_cap',0)+g.get('dp_transition_cap',0)!=len(cases):
        raise AssertionError('cap count mismatch')
    if len(cases)!=1:
        raise AssertionError('frozen single-cap target changed')
    baseline=result['capped_examples'][0]
    if baseline['tokens_sha256']!=cases[0]['tokens_sha256']:
        raise AssertionError('cap fingerprint mismatch')
    new_lo,new_hi=g['new_sector_lower'],g['new_sector_upper']
    for c in cases:
        if c['alternative']['status']=='exact':
            old_l,old_u=c['old_interval']
            alt_l,alt_u=c['alternative_interval']
            new_lo+=alt_l-old_l
            new_hi+=alt_u-old_u
    if not (g['new_sector_lower']<=new_lo<=new_hi<=g['new_sector_upper']):
        raise AssertionError('invalid aggregate tightening')
    return {
        'status':'PASS','archive_sha256':result['archive_sha256'],
        'producer_identity_verified':False,
        'trace_files':result['trace_files'],
        'global_proxy_rows':g['global_proxy'],
        'baseline_conditional_interval':[g['new_sector_lower'],g['new_sector_upper']],
        'alternative_conditional_interval':[new_lo,new_hi],
        'baseline_point_identified_rows':235076,
        'alternative_point_identified_rows':235076+sum(
            c['alternative']['status']=='exact' and c['alternative_interval'][0]==c['alternative_interval'][1]
            for c in cases),
        'cap_cases':cases,
        'evidence_tier':'unverified_historical_tracer_source_conditional_NOT_GPU_transactions',
        'hardware_mechanism_promoted':False,
    }

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('archive',nargs='?')
    p.add_argument('--selftest',action='store_true')
    a=p.parse_args()
    if a.selftest:
        print(json.dumps(selftest(),sort_keys=True))
    if a.archive:
        print(json.dumps(scan(a.archive),sort_keys=True,indent=2))
    elif not a.selftest:
        p.error('archive required')
