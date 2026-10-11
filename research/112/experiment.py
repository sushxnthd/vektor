"""Preregistered V112 two-event experiment, 192/96/36 seeds + seven directed."""
import json,random,subprocess
from pathlib import Path
from identity_validator import Event,validate,legacy,replay
ROOT=Path(__file__).resolve().parent
def generate(seed,surprise=False):
 r=random.Random(seed);k=r.randrange(24)
 c1=1 if k in (6,12,17,22) else 0
 t1=1 if k in (3,5,7,8,12,13,15,18,21) else 0
 w1=1 if k in (0,1,2,4,5,9,10,11,13,16,19,22) else 0
 lane1=1 if k in (8,14,15,20) else 0
 space=('L' if k%3==0 else ('S' if k%3==1 else 'G'))
 op0,op1=(('L','L') if k in (2,7,11,20) else ('S','L'))
 if k in (5,10,16):op0,op1='A','L'
 ep1=1 if k in (9,14,21) else 0
 size=r.choice((1,2,4,8,16));addr=0x1000+32*r.randrange(0,8)
 if surprise:size=r.choice((1,2,4,8,16));addr=r.choice((0,0x2000,0xfffffff0,(1<<64)-16))
 delta=32 if k in (7,11,15,17,23) else 0
 if addr+delta+size>1<<64:addr=(1<<64)-delta-size
 pc1=100 if k in (1,4,6,12,17,22) else 104
 return [Event(0,0,0,0,100,0,op0,space,addr,size,77),
         Event(c1,t1,w1,lane1,pc1,ep1,op1,space,addr+delta,size,4096)],k
def plans():return [('ordered',[[0],[1]]),('reversed',[[1],[0]]),('samewave',[[0,1]]),
 ('duplicate',[[0],[1],[1]]),('dropped',[[0]]),('empty',[[],[0],[1]])]
def serial(cases):
 s=[str(len(cases))]
 for ev,w in cases:
  for e in ev:s.append(f'{e.cid} {e.cta} {e.wid} {e.tid} {e.pc} {e.epoch} {e.op} {e.space} {e.addr} {e.size}')
  s.append(str(len(w)))
  for x in w:s.append(' '.join(map(str,[len(x)]+x)))
 return '\n'.join(s)+'\n'
def run():
 groups={'discovery':(112000,192),'holdout':(912000,96),'surprise':(712000,36)}
 cases=[];meta=[]
 for g,(start,n) in groups.items():
  for i in range(n):
   ev,k=generate(start+i,g=='surprise')
   for label,w in plans():cases.append((ev,w));meta.append((g,k,label))
 D=lambda c,cta,w,t,pc,ep,op,sp,addr,size:Event(c,cta,w,t,pc,ep,op,sp,addr,size,77)
 directed=[
  ('different_warp_private',[D(0,0,0,0,100,0,'S','L',4096,8),D(0,0,1,0,104,0,'L','L',4096,8)],[[1],[0]],True),
  ('same_thread_private',[D(0,0,0,0,100,0,'S','L',4096,8),D(0,0,0,0,104,0,'L','L',4096,8)],[[1],[0]],False),
  ('different_core_private',[D(0,0,0,0,100,0,'S','L',4096,8),D(1,0,0,0,104,0,'L','L',4096,8)],[[1],[0]],True),
  ('different_cta_reused_hart',[D(0,0,0,0,100,0,'S','L',4096,8),D(0,1,0,0,104,0,'L','L',4096,8)],[[1],[0]],True),
  ('same_cta_shared',[D(0,0,0,0,100,0,'S','S',4096,8),D(0,0,1,0,104,0,'L','S',4096,8)],[[1],[0]],False),
  ('global_conflict',[D(0,0,0,0,100,0,'S','G',4096,8),D(1,1,1,0,104,0,'L','G',4096,8)],[[1],[0]],False),
  ('mixed_cta_wave',[D(0,0,0,0,100,0,'L','S',4096,8),D(0,1,1,0,100,0,'L','S',4096,8)],[[0,1]],False)]
 for label,ev,w,expected in directed:cases.append((ev,w));meta.append(('directed',-1,label))
 subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','-pedantic',str(ROOT/'replica112.cpp'),'-o',str(ROOT/'replica112_bin')],check=True)
 cpp=subprocess.run([str(ROOT/'replica112_bin')],input=serial(cases),capture_output=True,text=True,check=True)
 truth=[x=='1' for x in cpp.stdout.splitlines()]
 assert len(truth)==len(cases)
 records=[]
 for (ev,w),(g,k,label),c in zip(cases,meta,truth):
  n=validate(ev,w);o=legacy(ev,w)
  assert n==c,(g,k,label,ev,w,n,c)
  if label=='ordered':assert n
  if label in ('duplicate','dropped','empty'):assert not n
  if label=='reversed' and n:assert replay(ev,[[0],[1]])==replay(ev,[[1],[0]])
  records.append({'group':g,'kind':k,'variant':label,'v111':o,'v112':n})
 for (label,ev,w,expected),row in zip(directed,records[-len(directed):]):
  assert row['v112']==expected,(label,row)
 def summ(x):return {'cases':len(x),'v111_accept':sum(z['v111'] for z in x),
  'v112_accept':sum(z['v112'] for z in x),
  'v111_overreject':sum(z['v112'] and not z['v111'] for z in x),
  'v111_accept_v112_reject':sum(z['v111'] and not z['v112'] for z in x)}
 result={'scope':'abstract SC host model, not GPU execution','matches':len(cases),
  'surprise_fraction':36/324,'groups':{g:summ([x for x in records if x['group']==g]) for g in [*groups,'directed']}}
 (ROOT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':run()
