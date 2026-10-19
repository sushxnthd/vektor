"""Synthetic, single-lookup-port MSHR admission model. Not silicon performance."""
import csv,json,random,heapq
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def trace(seed,count,skew):
    rng=random.Random(seed)
    for i in range(count):
        bank=0 if rng.random()<skew else rng.randrange(4)
        yield (i<<2)|bank
def run(tags,latency,banked):
    live=[];counts=[0]*4;cycle=0;stalls=0;issued=0
    for tag in tags:
        b=tag&3
        while True:
            while live and live[0][0]<=cycle:
                _,done=heapq.heappop(live);counts[done]-=1
            full=counts[b]>=4 if banked else len(live)>=16
            if not full:break
            stalls+=1;cycle+=1
        heapq.heappush(live,(cycle+latency,b))
        counts[b]+=1;issued+=1;cycle+=1
    return dict(cycles=cycle,stalls=stalls,requests=issued,throughput=issued/cycle if cycle else 0,comparison_lanes=4 if banked else 16)
def evaluate(seed,latency,skew,count=20000):
    tags=list(trace(seed,count,skew))
    base=run(tags,latency,False);cand=run(tags,latency,True)
    ratio=cand['throughput']/base['throughput']
    return dict(seed=seed,latency=latency,skew=skew,base_cycles=base['cycles'],cand_cycles=cand['cycles'],base_stalls=base['stalls'],cand_stalls=cand['stalls'],throughput_ratio=ratio,gain_pct=(ratio-1)*100,base_comparisons=16*count,cand_comparisons=4*count)
def main():
    frozen=[(22117,4,0.0),(22129,12,0.9),(22131,12,0.0)]
    holdout=[evaluate(*x) for x in frozen]
    assert holdout[0]['throughput_ratio']>=0.98
    assert holdout[1]['throughput_ratio']<=0.90
    assert holdout[2]['throughput_ratio']<1
    sweeps=[evaluate(seed,latency,skew,3000) for latency in (4,6,8,12,16) for skew in (0,0.25,0.5,0.9,1.0) for seed in (22143,22147,22151,22159,22163)]
    (ROOT/'evidence/holdout.json').write_text(json.dumps(holdout,indent=2)+'\n')
    with (ROOT/'evidence/sensitivity.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(sweeps[0]));w.writeheader();w.writerows(sweeps)
    print(json.dumps(dict(holdout=holdout,sensitivity_count=len(sweeps),frozen_predictions_pass=True),indent=2))
if __name__=='__main__':main()
