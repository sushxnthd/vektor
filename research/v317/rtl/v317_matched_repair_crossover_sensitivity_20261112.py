#!/usr/bin/env python3
"""Prospective matched-repair crossover sensitivity, not physical signoff.

Uses the *cross-run* historical numbers only as a deliberately non-validating
illustration. Final decisions MUST use matched, electrically legal measurements.
"""
from fractions import Fraction as F
from itertools import product

def score(service_ratio, area_compact, area_pairwise, period_compact, period_pairwise):
    """Pairwise/compact useful work per second per unit area."""
    assert min(service_ratio, area_compact, area_pairwise, period_compact, period_pairwise) > 0
    return service_ratio * area_compact * period_compact / (area_pairwise * period_pairwise)

def required_service(area_compact, area_pairwise, period_compact, period_pairwise, target=F(102,100)):
    return target * area_pairwise * period_pairwise / (area_compact * period_compact)

def evaluate():
    # Predeclared synthetic sweep, not a fit to any physical run.
    ac, ap = F('21314.6'), F('21324.7')
    tc, tp = F('2.24'), F('2.20')
    rows=[]
    for compact_repair_ps, pairwise_repair_ps in product((0,10,25,50), repeat=2):
        for service in (F(1),F('1.005'),F('1.02'),F('1.05')):
            pc=tc+F(compact_repair_ps,1000)
            pp=tp+F(pairwise_repair_ps,1000)
            ratio=score(service,ac,ap,pc,pp)
            rows.append((compact_repair_ps,pairwise_repair_ps,str(service),float(ratio),ratio>=F('1.02')))
    # Exact identities and counterexamples; never substitute for DRC/electrical legality.
    assert score(F(1),ac,ap,tc,tp) > 1
    assert score(F(1),ac,ap,tc,tp+F('0.05')) < 1
    assert required_service(ac,ap,tc,tp) > 1
    assert score(required_service(ac,ap,tc,tp),ac,ap,tc,tp)==F('1.02')
    assert score(F('1.02'),ac,ap,tc,tp+F('0.05')) < F('1.02')
    assert len(rows)==64
    return rows

if __name__=='__main__':
    import csv,sys
    out=csv.writer(sys.stdout)
    out.writerow(('compact_repair_ps','pairwise_repair_ps','service_ratio','throughput_per_area_ratio','meets_2pct_gate'))
    out.writerows(evaluate())
