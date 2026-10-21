#!/usr/bin/env python3
"""V269 training-only two-class response-queue sweep. E1, not physical PPA."""
import random,json,itertools,collections
def run(seed=269000,kind='split',T=10000,offered=.85,slow_frac=.3,blocked=.75,period=16,fast_burst=False):
 rng=random.Random(seed)
 q=[collections.deque(),collections.deque()] if kind=='split' else collections.deque()
 incoming=[collections.deque(),collections.deque()]
 accepted=done=blocked_in=0;delivered=[0,0];arrivals=[0,0];rr=0;delay_sum=0
 for t in range(T):
  if rng.random()<offered:
   cls=0 if rng.random()<slow_frac else 1
   incoming[cls].append((t,cls));arrivals[cls]+=1
  ready0=(t%period)/period>=blocked
  if fast_burst and t%64<10:ready0=False;ready1=False
  else:ready1=True
  if kind=='split':
   choices=[i for i in (0,1) if q[i] and (ready0 if i==0 else ready1)]
   if choices:
    c=choices[0] if len(choices)==1 else rr
    if c not in choices:c=choices[0]
    a,_=q[c].popleft();done+=1;delivered[c]+=1;delay_sum+=t-a;rr=1-c
  else:
   depth={'fifo':1,'look2':2,'greedy':len(q)}[kind]
   chosen=None
   for j in range(min(depth,len(q))):
    if ready0 if q[j][1]==0 else ready1:
     chosen=j;break
   if chosen is not None:
    a,c=q[chosen];del q[chosen];done+=1;delivered[c]+=1;delay_sum+=t-a
  cand=[]
  for c in (0,1):
   if incoming[c]:
    has_space=len(q[c])<4 if kind=='split' else len(q)<8
    if has_space:cand.append((incoming[c][0][0],c))
  if cand:
   _,c=min(cand);item=incoming[c].popleft()
   (q[c] if kind=='split' else q).append(item);accepted+=1
  elif any(incoming):blocked_in+=1
 return {'completed':done,'accepted':accepted,'offered':sum(arrivals),'slow_completed':delivered[0],'fast_completed':delivered[1],'backpressure_cycles':blocked_in,'mean_latency':round(delay_sum/done,3) if done else None}
rows=[]
for blocked,slow_frac,offered,burst in itertools.product([0,.25,.5,.75],[.1,.3,.5],[.6,.85],[False,True]):
 cfg={'seed':269000,'T':10000,'offered':offered,'slow_frac':slow_frac,'blocked':blocked,'fast_burst':burst}
 out={k:run(kind=k,**cfg) for k in ('fifo','look2','greedy','split')}
 rows.append({'blocked':blocked,'slow_frac':slow_frac,'offered':offered,'fast_burst':burst,'split_vs_look2':round(out['split']['completed']/max(out['look2']['completed'],1),5),'split_vs_greedy':round(out['split']['completed']/max(out['greedy']['completed'],1),5),'data':out})
res={'kernel':'V269','evidence':'E1 exploratory only','rows':rows,'wins_over_look2_5pct':sum(x['split_vs_look2']>1.05 for x in rows),'warning':'Greedy is not global admission oracle; physical controls unresolved; holdouts unopened'}
print(json.dumps(res,indent=2))
