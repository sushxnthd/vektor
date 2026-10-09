#!/usr/bin/env python3
import json
from sim_070 import simulate
rows=[]
for i in range(24):
    opts=dict(seed=101+i,cycles=10000,uid_bits=1+i%3,
              timeout=2+(i%4)*3,latency=9+(i%10),
              jitter=8+(i%7),ack_loss=.2+.04*(i%5),
              data_loss=.05,clone_p=.75)
    for policy in ("strong","early"):
        rows.append(simulate(**opts,policy=policy))
for i in range(12):
    rows.append(simulate(seed=501+i,cycles=10000,uid_bits=1+i%3,
              timeout=3+i%6,latency=7+i%5,jitter=9,
              ack_loss=.3,clone_p=.9,reset_at=3300,policy="strong"))
strong=[r for r in rows if r["policy"]=="strong"]
early=[r for r in rows if r["policy"]=="early"]
assert len(strong)==36 and len(early)==24
p1=all(r["retirements"]>0 and not(r["false_data"] or r["false_ack"]) for r in strong)
p2=any(r["false_data"] or r["false_ack"] for r in early)
p3=all(not(r["false_data"] or r["false_ack"]) for r in strong if r["reset_at"]>=0)
assert p1 and p2 and p3
summary=dict(P1=p1,P2=p2,P3=p3,strong_runs=len(strong),early_runs=len(early),
             early_unsafe_runs=sum(bool(r["false_data"] or r["false_ack"]) for r in early),
             early_false_data=sum(r["false_data"] for r in early),
             early_false_ack=sum(r["false_ack"] for r in early),
             strong_retirements=sum(r["retirements"] for r in strong))
with open("research/070/holdout_results_070.json","w") as f:
    json.dump(dict(summary=summary,runs=rows),f,indent=2)
print(json.dumps(summary,indent=2))
