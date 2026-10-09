#!/usr/bin/env python3
"""Vektor-055 model grid and 64-seed exploratory PTX-mix holdout."""
import csv,tempfile
from pathlib import Path
from generate_055 import generate
from check_055 import check
root=Path(__file__).resolve().parents[1]
(root/'build').mkdir(exist_ok=True);(root/'results').mkdir(exist_ok=True)
records=[]
for mode in ('zero','ptx','synth25','synth50','maskstress'):
    for seed in (550055,550056,550057,550058):
        pair=[]
        for dedup in (0,1):
            p=root/'build'/f'{mode}_s{seed}_d{dedup}.vec'
            x=generate(p,dedup,seed,1500,mode)
            check(p,dedup);records.append(x);pair.append(x)
        if mode=='zero':assert pair[0]['reads']==pair[1]['reads'] and pair[0]['completions']==pair[1]['completions']
        assert pair[0]['error']==pair[1]['error']==1
with (root/'results'/'model_runs_055.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,records[0]);w.writeheader();w.writerows(records)
for mode in ('zero','ptx','synth25','synth50','maskstress'):
    r=[x for x in records if x['mode']==mode]
    print(mode,[(d,sum(x['completions'] for x in r if x['dedup']==d)) for d in (0,1)])
rows=[]
with tempfile.TemporaryDirectory() as d:
    for seed in range(555000,555064):
        a=generate(Path(d)/'a.vec',0,seed,3000,'ptx')
        b=generate(Path(d)/'b.vec',1,seed,3000,'ptx')
        rows.append(dict(seed=seed,base_reads=a['reads'],dedup_reads=b['reads'],base_completions=a['completions'],dedup_completions=b['completions'],completion_delta=b['completions']-a['completions']))
with (root/'results'/'holdout_055.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,rows[0]);w.writeheader();w.writerows(rows)
print('PASS',len(records),'RTL reference traces, 60000 cycles; 64 heldout seed pairs')
