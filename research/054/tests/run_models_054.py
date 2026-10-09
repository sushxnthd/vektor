#!/usr/bin/env python3
"""Run model-level differential tests. Does not run HDL simulation."""
import csv, pathlib
from generate_054 import generate
from replicate_054 import run
root=pathlib.Path(__file__).resolve().parents[1]
(root/'build').mkdir(exist_ok=True)
(root/'results').mkdir(exist_ok=True)
records=[]
for seed in (540054,540055,540056):
    for alias in (0,25,50,100):
        for dedup in (0,1):
            path=root/'build'/f'd{dedup}_a{alias}_s{seed}.vec'
            d=generate(path,dedup,seed,2500,alias)
            assert run(path,dedup)==2500
            records.append(d)
with open(root/'results'/'model_runs_054.csv','w',newline='') as f:
    w=csv.DictWriter(f,records[0].keys());w.writeheader();w.writerows(records)
for alias in (0,25,50,100):
    pairs=[(next(x for x in records if x['seed']==seed and x['alias_pct']==alias and x['dedup']==0),
            next(x for x in records if x['seed']==seed and x['alias_pct']==alias and x['dedup']==1))
           for seed in (540054,540055,540056)]
    print(f'alias={alias}: baseline_reads={[a["reads"] for a,b in pairs]} dedup_reads={[b["reads"] for a,b in pairs]} '
          f'baseline_completions={[a["completions"] for a,b in pairs]} dedup_completions={[b["completions"] for a,b in pairs]}')
    if alias==0:
        assert all(a['reads']==b['reads'] and a['completions']==b['completions'] for a,b in pairs)
assert all(x['error']==1 for x in records), 'malformed return not detected'
print('PASS 24 independent replica traces, 60,000 cycles; 0% alias exact-control')
