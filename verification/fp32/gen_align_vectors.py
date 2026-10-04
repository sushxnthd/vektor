import random, pathlib
random.seed(2702774281)
out=pathlib.Path("build/rtl"); out.mkdir(parents=True,exist_ok=True)
def align(sig,d):
    if d<=0:return sig,0
    if d>=56:return 0,int(sig!=0)
    return sig>>d,int(bool(sig&((1<<d)-1)))
rows=[]
for _ in range(20000):
    pe=random.randint(-298,254); ce=random.randint(-149,127)
    pm=random.getrandbits(48); cm=random.getrandbits(24); e=max(pe,ce)
    pa,ps=align(pm,e-pe); ca,cs=align(cm,e-ce)
    rows.append((pe,pm,ce,cm,pa,ca,ps,cs))
with open(out/"fp32_align_vectors.txt","w") as f:
    for r in rows:f.write(f"{r[0]} {r[1]:012x} {r[2]} {r[3]:06x} {r[4]:014x} {r[5]:014x} {r[6]} {r[7]}\n")
print("FP32_ALIGN_GEN",len(rows))
