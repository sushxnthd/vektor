"""Independent C++/Python comparison. Generates no paid calls."""
import json,random,subprocess
from pathlib import Path
from final_return_model import run
HERE=Path(__file__).resolve().parent
BIN=HERE/'replicate_final_bin'
subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra',str(HERE/'replicate_final.cpp'),'-o',str(BIN)],check=True)
fields=['admitted','stalls','correct','false','stale','ignored','max_queue','max_age','delivered']
comparisons=0
for seed in range(128):
    rng=random.Random(94000+seed)
    tags=rng.choice((1,2,4,8));width=rng.choice((1,2,4))
    policy=rng.choice(('first','final'));guard=rng.choice((0,1,3))
    T=rng.choice((128,256,512));steps=[]
    for t in range(T):
        steps.append(dict(offer=rng.random()<.83,latency=rng.randint(1,7),
            copies=rng.randint(1,4),spacing=rng.randint(1,5),
            cancel_mask=rng.randrange(1<<tags) if rng.random()<.03 else 0,
            soft_reset=rng.random()<.005,
            duplicate_final_delta=rng.randint(1,9) if rng.random()<.07 else None))
    lines=[f'{T} {tags} {width} {int(policy=="final")} {guard}']
    for s in steps:
        d=s['duplicate_final_delta']
        lines.append(f'{int(s["offer"])} {s["latency"]} {s["copies"]} {s["spacing"]} {s["cancel_mask"]} {int(s["soft_reset"])} {d if d is not None else -1}')
    out=subprocess.check_output([str(BIN)],input='\n'.join(lines)+'\n',text=True)
    actual=list(map(int,out.strip().split()))
    expected=run(steps,tags,width,policy,guard).metrics
    for field,a in zip(fields,actual):
        assert a==expected[field],(seed,field,a,expected[field])
        comparisons+=1
print(json.dumps({'seeds':128,'metric_comparisons':comparisons,'status':'PASS'}))
