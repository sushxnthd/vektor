import json
from pathlib import Path
from final_return_model import run
from sweep import make
rows=[]
for i in range(80):
    tags,width,steps=make(990000+i,surprise=i<10)
    a=run(steps,tags,width,'final').metrics
    b=run(steps,tags,width,'final',suppress_nonfinal=True).metrics
    rows.append({'seed':990000+i,'surprise':i<10,'tags':tags,'width':width,
        'all_admitted':a['admitted'],'filtered_admitted':b['admitted'],
        'all_false':a['false'],'filtered_false':b['false'],
        'all_max_queue':a['max_queue'],'filtered_max_queue':b['max_queue']})
summary={'n':len(rows),'improved':sum(r['filtered_admitted']>r['all_admitted'] for r in rows),
    'tied':sum(r['filtered_admitted']==r['all_admitted'] for r in rows),
    'regressed':sum(r['filtered_admitted']<r['all_admitted'] for r in rows),
    'unsafe_all':sum(r['all_false']>0 for r in rows),
    'unsafe_filtered':sum(r['filtered_false']>0 for r in rows),
    'mean_paired_admission_ratio':sum(r['filtered_admitted']/max(1,r['all_admitted']) for r in rows)/len(rows)}
Path(__file__).with_name('holdout_c.json').write_text(json.dumps({'summary':summary,'rows':rows},indent=2)+'\n')
print(json.dumps(summary,indent=2))
