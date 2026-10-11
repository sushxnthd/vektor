"""Deterministic synthetic experiments; run python sweep.py discovery|surprise|holdout."""
import itertools,json,random,sys
from joint_cost import Config,run
def discovery():
    return [Config(pattern=p,length=l,rf_ports=rp,migration_bw=mb,memory_stride=ms,locality=loc)
      for p,l,rp,mb,ms,loc in itertools.product(
      ('coherent','balanced','minority','four_path'),(1,4,16,32),(2,8),(8,64),(0,1),('warp_local','path_striped'))]
def random_configs(n,seed):
    r=random.Random(seed);out=[]
    for i in range(n):
        w=r.choice([4,8,16])
        out.append(Config(pattern=r.choice(['coherent','balanced','minority','four_path','random']),
          length=r.choice([1,2,4,8,16,32]),warps=w,window=min(w,r.choice([2,4,8,16])),
          banks=r.choice([8,16,32]),rf_ports=r.choice([1,2,4,8]),
          migration_bw=r.choice([4,8,32,128]),setup=r.choice([0,4,12]),
          memory_stride=r.choice([0,1,4]),memory_ports=r.choice([1,2,8]),
          locality=r.choice(['warp_local','path_striped','random']),seed=seed+i))
    return out
def main():
    mode=sys.argv[1]
    configs={'discovery':discovery(),'surprise':random_configs(32,202),
             'holdout':random_configs(96,9102)}[mode]
    rows=[run(c) for c in configs]
    totals={'n':len(rows),'win':sum(x['speedup']>1 for x in rows),
      'loss':sum(x['speedup']<1 for x in rows),
      'tie':sum(x['speedup']==1 for x in rows),
      'heuristic_regressions':sum(x['totals']['heuristic']>x['totals']['ipdom'] for x in rows)}
    with open(mode+'.json','w') as f:json.dump({'summary':totals,'rows':rows},f,indent=2)
    print(totals)
if __name__=='__main__':main()
