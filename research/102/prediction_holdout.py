"""Unseen model-derived sign predictions, frozen in PREDICTION_2_PREREG.md."""
import json
from joint_cost import Config,run
def main():
    rows=[]
    for warps in (8,16):
        for window in (4,8):
            for length in (12,24):
                for ports in (1,2,3,4,5,6,8):
                    c=Config(pattern='balanced',warps=warps,window=window,length=length,
                             rf_ports=ports,migration_bw=8,setup=4,memory_stride=0)
                    r=run(c)
                    prediction='loss' if ports<=3 else 'win'
                    observed='loss' if r['speedup']<1 else ('win' if r['speedup']>1 else 'tie')
                    rows.append({'config':r['config'],'predicted':prediction,'observed':observed,
                                 'ipdom':r['totals']['ipdom'],'compacted':r['totals']['dwf']})
    result={'n':len(rows),'predictions_correct':sum(x['predicted']==x['observed'] for x in rows),'rows':rows}
    with open('prediction_holdout.json','w') as f:json.dump(result,f,indent=2)
    print('prediction:',result['predictions_correct'],'/',result['n'])
    assert result['predictions_correct']==result['n']
if __name__=='__main__':main()
