"""Vektor-087 held-out synthetic deadline lead-time scaling-law test."""
from reservation_reference_087 import Calendar
import json

out=[]
for short in range(1,5):
    for long in range(short+1,6):
        model=Calendar(1,2,5,1)
        count=[0,0]
        for _ in range(1000):
            grants,_=model.step(False,[1,1],[0,0],[short,long])
            count=[a+b for a,b in zip(count,grants)]
        predicted=[long-short,1000]
        assert count==predicted,(short,long,count)
        out.append(dict(latencies=[short,long],prediction=predicted,simulation=count,residual=[0,0]))
print(json.dumps(out,indent=2))
