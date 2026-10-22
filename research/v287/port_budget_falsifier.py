#!/usr/bin/env python3
"""V287: architecture-level upper bound, not an electrical PPA result."""
import json,re,pathlib
root=pathlib.Path(__file__).resolve().parents[2]
spec=json.loads((root/'specs/vektor1a.json').read_text())
arb=(root/'rtl/vtile/rf_bank_arbiter.sv').read_text()
issue=(root/'rtl/vtile/issue_control.sv').read_text()
assert re.search(r'output\s+reg\s+\[3:0\]\s+grant',arb)
assert re.search(r'output\s+wire\s+\[3:0\]\s+issue_valid',issue)
assert spec['schedulers_per_tile']==4
assert spec['fp32_lanes_per_tile']//spec['wave_size']==4
n=spec['schedulers_per_tile']
rows=[]
for rf in range(1,5):
    # All four grant bits refer to distinct wave operand requests.
    # Fusion still consumes TWO such requests per fused issue.
    base=min(n,rf)
    fused=min(2*n,rf)
    assert base==fused
    rows.append({'wave_grants_per_cycle':rf,'baseline_wave_ops_upper_bound':base,
                 'fused_wave_ops_upper_bound':fused,'ideal_gain_bound':fused/base})
print(json.dumps({'status':'V287 conditional integrated-tile issue-throughput upper bound',
 'assumptions':['one grant per wave operand set','four schedulers drive four wave32 SIMD issue slots',
                'no added RF ports, operand cache read bandwidth, or ALU lanes'],
 'rows':rows,'max_gain':1.0,
 'qualification':'Upper bound under saturation; not actual performance or electrical STA.'},indent=2))
