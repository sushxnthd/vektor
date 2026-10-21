"""V271 request-side MSHR credit model; stdlib-only; E1 evidence."""
import argparse, json, random, hashlib, statistics
MODES={'fixed44':(4,4,0),'fixed53':(5,3,0),'fixed35':(3,5,0),
       'fixed62':(6,2,0),'fixed26':(2,6,0),'hybrid':(3,3,2),'global':(0,0,8)}
def offered(profile,seed,cycles):
    rng=random.Random(seed)
    schedule=[[],[]]
    for t in range(cycles):
        if profile=='alternating':
            phase=(t//360)%2
            a,b=((5,1) if phase==0 else (1,5)) if t%36==0 else (0,0)
            if a+b and rng.random()<.10:
                if phase==0:a+=rng.choice([-1,1])
                else:b+=rng.choice([-1,1])
        elif profile=='balanced':
            a,b=(4,4) if t%36==0 else (0,0)
            if a+b and rng.random()<.10:a+=rng.choice([-1,1])
        elif profile=='single_skew':
            a,b=(7,0) if t%36==0 else (0,0)
            if a and rng.random()<.10:a+=rng.choice([-1,1])
        elif profile=='divergent':
            a,b=((rng.randrange(6),rng.randrange(6)) if t%36==0 else (0,0))
        else:raise ValueError(profile)
        schedule[0].extend([t]*a);schedule[1].extend([t]*b)
    return schedule
def run(mode,profile='alternating',seed=271001,cycles=3600,latency=30):
    ca,cb,cs=MODES[mode]
    arrivals=offered(profile,seed,cycles)
    q=[[],[]];index=[0,0];live=[];shared_busy=0;local=[0,0]
    done=[];accepted=[0,0];maxq=0;stall=0
    for t in range(cycles+100000):
        if t>=cycles and not live and not q[0] and not q[1] and index==[len(arrivals[0]),len(arrivals[1])]:
            break
        keep=[]
        for due,klass,bucket,birth in live:
            if due==t:
                if bucket=='shared':shared_busy-=1
                else:local[klass]-=1
                done.append((t-birth,klass))
            else:keep.append((due,klass,bucket,birth))
        live=keep
        for k in (0,1):
            while index[k]<len(arrivals[k]) and arrivals[k][index[k]]<=t:
                q[k].append(arrivals[k][index[k]]);index[k]+=1
        shared_issued=False
        for k in (0,1):
            if not q[k]:continue
            if mode=='global':bucket='shared' if shared_busy<cs else None
            else:
                limit=ca if k==0 else cb
                if local[k]<limit:bucket='local'
                elif shared_busy<cs and not shared_issued:bucket='shared'
                else:bucket=None
            if bucket is None:stall+=1;continue
            birth=q[k].pop(0)
            if bucket=='shared':shared_busy+=1;shared_issued=True
            else:local[k]+=1
            live.append((t+latency,k,bucket,birth));accepted[k]+=1
        maxq=max(maxq,len(q[0])+len(q[1]))
        assert local[0]<=ca and local[1]<=cb and shared_busy<=cs
        assert local[0]+local[1]+shared_busy<=8
    n=t+1
    assert len(done)==sum(accepted)
    assert accepted==[len(x) for x in arrivals]
    lat=[x[0] for x in done]
    return dict(mode=mode,profile=profile,seed=seed,cycles=cycles,service_latency=latency,
        completed=len(done),offered=len(arrivals[0])+len(arrivals[1]),
        mean_completion_latency=round(statistics.mean(lat),4),
        p95_completion_latency=sorted(lat)[int(.95*(len(lat)-1))],
        peak_pending=maxq,stall_events=stall,throughput=round(len(done)/n,6))
def sweep():
    return [run(m,p,271001,3600,l)
        for p in ('alternating','balanced','single_skew','divergent')
        for l in (12,24,30,42) for m in MODES]
def frozen():
    entries=[
      dict(name='positive',profile='alternating',seed=271901,cycles=7200,latency=30,
           prediction='hybrid lower mean latency than every fixed partition; global no worse'),
      dict(name='no_win',profile='balanced',seed=271902,cycles=7200,latency=12,
           prediction='hybrid no better than fixed44'),
      dict(name='loss',profile='single_skew',seed=271903,cycles=7200,latency=42,
           prediction='hybrid worse than fixed62 and global')]
    payload=json.dumps(entries,sort_keys=True,separators=(',',':'))
    return dict(entries=entries,sha256=hashlib.sha256(payload.encode()).hexdigest(),holdouts_evaluated=False)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--sweep',action='store_true');ap.add_argument('--freeze',action='store_true')
    args=ap.parse_args()
    print(json.dumps(sweep() if args.sweep else frozen(),indent=2))