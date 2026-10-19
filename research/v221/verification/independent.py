"""Independent cycle-by-cycle list reference; exhaustive small traces."""
import json
from itertools import product
def ref(tags,latency,banked):
    retire=[];t=0;stalls=0
    for tag in tags:
        while True:
            retire=[(due,b) for due,b in retire if due>t]
            bank=tag&3
            if (sum(b==bank for _,b in retire)<4 if banked else len(retire)<16):
                retire.append((t+latency,bank));t+=1;break
            stalls+=1;t+=1
    return t,stalls
def check():
    from model.sweep import run
    n=0
    for length in range(8):
        for banks in product(range(4),repeat=length):
            for latency in (1,2,4,8,12):
                for banked in (False,True):
                    expected=ref(banks,latency,banked)
                    observed=run(banks,latency,banked)
                    assert expected==(observed['cycles'],observed['stalls'])
                    n+=1
    print(json.dumps(dict(independent_checks=n,mismatches=0)))
if __name__=='__main__':check()
