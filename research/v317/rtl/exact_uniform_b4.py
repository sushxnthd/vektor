#!/usr/bin/env python3
"""Post-freeze exhaustive four-bank independent distribution check."""
import itertools,json
from audit_bank_service_oracle import greedy_count,recursive_opt
def run():
 n=gs=ms=improved=0
 for seq in itertools.product(range(4),repeat=8):
  reqs=list(zip(seq[::2],seq[1::2]))
  g=greedy_count(reqs,15);m=recursive_opt(reqs,15)
  assert 0<=m-g<=1
  gs+=g;ms+=m;improved+=(m>g);n+=1
 assert n==65536 and gs>0
 assert abs(ms/gs-(1+(improved/n)/(gs/n)))<1e-12
 return dict(batches=n,greedy_grants=gs,oracle_grants=ms,
  improved_batches=improved,ratio=ms/gs,
  exact_law=1+(improved/n)/(gs/n))
if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
