from pathlib import Path
import random,json,hashlib
from model_058 import Queue
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
OUT.mkdir(exist_ok=True)
def sequence(seed,cycles=140):
 rng=random.Random(seed);q=Queue();lines=[];next_tag=1
 stalls=full_push_pop=saturated_age_cycles=0
 for c in range(cycles):
  valid=int((rng.random()<(0.87 if seed%4 else 0.45)) and next_tag<250)
  ready=int(rng.random()<(0.72 if seed%7 else 0.25))
  if c%41 in range(11,20):ready=0
  rem=1+rng.randrange(3)
  tag=next_tag
  data=(tag*137+seed*11)&65535
  before_full=(len(q.q)==4)
  saturated_age_cycles+=int(any(e.age==15 for e in q.q))
  obs=q.step(valid,tag,data,rem,ready)
  full_push_pop+=int(before_full and valid and ready and obs[0] and obs[1])
  if valid and obs[0]:next_tag+=1
  if obs[1] and not ready:stalls+=1
  lines.append(' '.join(map(str,[valid,tag,data,rem,ready,*obs])))
 assert len(q.accepted)==len(q.served)+len(q.q)
 return lines,dict(seed=seed,cycles=cycles,accepted=len(q.accepted),served=len(q.served),pending=len(q.q),stalls=stalls,full_push_pop=full_push_pop,saturated_age_cycles=saturated_age_cycles)
def main():
 seeds=list(range(64))+list(range(1000,1008))
 lines=[];summaries=[]
 for seed in seeds:
  l,s=sequence(seed)
  lines+=['-1 0 0 0 0 0 0 0 0 0']+l
  summaries.append(s)
 path=OUT/'vectors_058.txt'
 path.write_text('\n'.join(lines)+'\n')
 summary=dict(configurations=len(seeds),data_cycles=sum(s['cycles'] for s in summaries),vector_lines=len(lines),accepted=sum(s['accepted'] for s in summaries),served=sum(s['served'] for s in summaries),stalled_cycles=sum(s['stalls'] for s in summaries),full_push_pop=sum(s['full_push_pop'] for s in summaries),saturated_age_cycles=sum(s['saturated_age_cycles'] for s in summaries),probe_fraction=8/len(seeds),vector_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
 (OUT/'model_summary_058.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
