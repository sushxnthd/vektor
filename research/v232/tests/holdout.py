import random,json
rows=[]
for mask,seed,expected in [(1,49231,0.375),(5,36103,0.625),(15,91611,1.125)]:
 r=random.Random(seed);last=0;trans=0
 for _ in range(2048):
  x=r.getrandbits(8);trans+=(x^last).bit_count();last=x
 baseline=32*trans
 candidate=(4+8*mask.bit_count())*trans
 ratio=candidate/baseline
 assert abs(ratio-expected)<1e-12
 rows.append(dict(mask=mask,baseline=baseline,candidate=candidate,ratio=ratio))
print(json.dumps(rows,indent=2))
