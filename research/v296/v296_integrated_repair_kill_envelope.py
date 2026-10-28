#!/usr/bin/env python3
"""Integrated V296 fixed-path repair envelope. Not a physical repair.
Original routed run: https://github.com/sushxnthd/vektor/actions/runs/40675850164
No D4/D8 deferred-write results are mixed with this integrated tile experiment.
"""
from decimal import Decimal as D
from fractions import Fraction
import json

PERIOD=D('3500')
GUARD=D('250')
BUDGET=D('30000')
ORIGINAL={
 'pairwise':dict(area=D('17857.644252'),setup=D('-1047.895'),hold=D('-36.622'),cap=3,slew=0),
 'serial':dict(area=D('18953.830505'),setup=D('-1859.922'),hold=D('-19.796'),cap=3,slew=0),
}

def check(name,setup=0,hold=0,caps=0,area=0,period=PERIOD,adverse_setup=0,adverse_hold=0):
 x=ORIGINAL[name]
 s=x['setup']+D(str(setup))-D(str(adverse_setup))+D(str(period))-PERIOD
 h=x['hold']+D(str(hold))-D(str(adverse_hold))
 a=x['area']+D(str(area))
 c=max(0,x['cap']-int(caps))
 return dict(setup_ps=s,hold_ps=h,cap_violations=c,area_um2=a,
             slices=int(BUDGET//a) if a>0 else 0,
             feasible=s>=GUARD and h>=0 and c==0 and x['slew']==0 and a<=BUDGET)

def minimum(name,adverse_setup=0,adverse_hold=0):
 x=ORIGINAL[name]
 return dict(setup_recovery_ps=GUARD-x['setup']+D(str(adverse_setup)),
             hold_recovery_ps=-x['hold']+D(str(adverse_hold)),
             cap_violations_to_fix=x['cap'],
             area_overhead_ceiling_um2=BUDGET-x['area'],
             setup_only_clock_period_ps=PERIOD+GUARD-x['setup'])

SCENARIOS=[
 ('clock_only_6ns',dict(period=6000),False),
 ('symmetric_1500ps_setup_only',dict(setup=1500),False),
 ('symmetric_2200ps_all_checks_counterfactual',dict(setup=2200,hold=40,caps=3,area=1000),True),
 ('symmetric_2200ps_100ps_adverse',dict(setup=2200,hold=140,caps=3,area=1000,adverse_setup=100,adverse_hold=100),False),
 ('symmetric_2210ps_100ps_adverse',dict(setup=2210,hold=140,caps=3,area=1000,adverse_setup=100,adverse_hold=100),True),
]

def independent_check():
 # Exact-rational threshold check and independent 1-ps brute-force boundary search.
 for name,x in ORIGINAL.items():
  s=Fraction(str(x['setup'])); h=Fraction(str(x['hold'])); g=Fraction(str(GUARD))
  first=next(i for i in range(2500) if s+i>=g)
  first_hold=next(i for i in range(100) if h+i>=0)
  assert first-1<g-s<=first
  assert first_hold-1< -h<=first_hold
  assert Fraction(str(minimum(name)['setup_recovery_ps']))==g-s
  assert check(name,setup=first,hold=first_hold,caps=3)['feasible']
  assert not check(name,setup=first-1,hold=first_hold,caps=3)['feasible']
  assert not check(name,setup=first,hold=first_hold-1,caps=3)['feasible']
  assert not check(name,setup=first,hold=first_hold,caps=2)['feasible']
  assert not check(name,period=10000)['feasible'] # clock-only leaves hold and cap broken
 return True

def evaluate():
 assert independent_check()
 scenarios=[]
 for name,kwargs,expected in SCENARIOS:
  outcomes={v:check(v,**kwargs) for v in ORIGINAL}
  both=all(o['feasible'] for o in outcomes.values())
  assert both==expected,name
  scenarios.append(dict(name=name,both_feasible_counterfactual=both,outcomes=outcomes))
 return dict(source_run=40675850164,evidence_tier='FIXED_PATH_ARITHMETIC_NOT_PHYSICAL_REPAIR',
             clock_ps=PERIOD,setup_guard_ps=GUARD,area_budget_um2=BUDGET,
             necessary_repair={k:minimum(k) for k in ORIGINAL},
             scenarios=scenarios,matched_physical_win=False,
             matched_equal_clock_admission_ratio_if_repaired='1.0 (conditional)',
             caution='All recovery scenarios are assumed path shifts; no RTL or extracted-RC repair performed. Path migration, hold, capacitance, DRC, energy, and shared ports require measurement.')

if __name__=='__main__':
 print(json.dumps(evaluate(),default=str,sort_keys=True,indent=2))
