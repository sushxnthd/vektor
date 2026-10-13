"""Reproduce frozen V147 RF-latency wildcard probes (software simulation)."""
import json
from fma_tile_model import run

def suite():
    out=[]
    for kind in ('bankhot','bankhot_indep','mixed'):
        for latency in (1,4,8):
            for stall in (.08,.25):
                for mapping in ('low','xor'):
                    out.append(run(seed=271828,kind=kind,count=128,ports=2,rf_latency=latency,stall_prob=stall,bank_map=mapping))
    return out

if __name__=='__main__':
    print(json.dumps(suite(),indent=2))
