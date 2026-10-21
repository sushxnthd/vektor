#!/usr/bin/env python3
"""Independent V262 oracle. Test-only, deliberately separate from generator."""
import importlib.util,random,json
from pathlib import Path
p=Path(__file__).with_name("v262_discriminator.py")
spec=importlib.util.spec_from_file_location("candidate",p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rng=random.Random(72620001)
checks=0
def check(a):
    global checks
    # Independent eligibility criterion using signed integer deltas.
    expected=all((-16<=a[k]-a[0]<=15) for k in (1,2,3))
    beats=m.packet(a)
    assert (len(beats)==1)==expected,(a,beats)
    if expected:
        payload=beats[0][1]
        assert payload>>31==0
        b=payload>>15&65535
        ds=[]
        for shift in (10,5,0):
            x=payload>>shift&31
            ds.append(x-32 if x>=16 else x)
        reconstructed=(b,b+ds[0],b+ds[1],b+ds[2])
    else:
        assert len(beats)==2
        reconstructed=(beats[0][1]>>16,beats[0][1]&65535,
                       beats[1][1]>>16,beats[1][1]&65535)
    assert reconstructed==a,(a,reconstructed)
    checks+=1

# Exhaustive reduced-domain tuples: 0..11 inclusive, all 12^4 groups.
for a0 in range(12):
 for a1 in range(12):
  for a2 in range(12):
   for a3 in range(12):
    check((a0,a1,a2,a3))
# Adversarial edge boundaries for 16-bit signed-difference eligibility.
edge=[0,1,15,16,17,31,32,32767,32768,65518,65519,65520,65534,65535]
for a0 in edge:
 for a1 in edge:
  for a2 in edge:
   check((a0,a1,a2,a0))
for _ in range(100000):
 check(tuple(rng.randrange(65536) for _ in range(4)))
print(json.dumps({"checks":checks,"failures":0,"kind":"independent_python_bitfield_oracle",
"not_RTL_simulation":True},sort_keys=True))
