import json,random
from pathlib import Path
from final_return_model import run
HERE=Path(__file__).resolve().parent

def make(seed,surprise=False,single=False):
    rng=random.Random(seed)
    if surprise:
        tags=rng.choice((1,2,3,4,8,16));width=rng.choice((1,2,3,4,8))
        horizon=rng.choice((96,256,512,1024));offer_rate=rng.uniform(.1,1)
        latmax=rng.randint(1,20);copymax=rng.randint(1,6);spacemax=rng.randint(1,12)
    else:
        tags=rng.choice((1,2,4));width=rng.choice((1,2))
        horizon=1024;offer_rate=rng.choice((.65,.9,1.))
        latmax=rng.choice((2,4,8))
        copymax=1 if single else rng.choice((2,3,4))
        spacemax=rng.choice((2,4,8))
    steps=[]
    for t in range(horizon):
        steps.append(dict(offer=rng.random()<offer_rate,latency=rng.randint(1,latmax),
            copies=1 if single else rng.randint(1,copymax),spacing=rng.randint(1,spacemax),
            cancel_mask=(1<<rng.randrange(tags)) if rng.random()<.012 else 0,
            soft_reset=rng.random()<.002))
    return tags,width,steps

def batch(count,probes,seedbase):
    rows=[]
    for i in range(count):
        surprise=i<probes
        tags,width,steps=make(seedbase+i,surprise)
        a=run(steps,tags,width,'first').metrics
        b=run(steps,tags,width,'final').metrics
        c=run(steps,tags,width,'final',suppress_nonfinal=True).metrics
        rows.append({'seed':seedbase+i,'surprise':surprise,'tags':tags,'width':width,
            'first_false':a['false'],'final_false':b['false'],
            'first_admitted':a['admitted'],'final_admitted':b['admitted'],
            'filtered_false':c['false'],'filtered_admitted':c['admitted'],
            'filtered_max_queue':c['max_queue'],'first_max_age':a['max_age'],
            'final_max_age':b['max_age'],'first_max_queue':a['max_queue'],
            'final_max_queue':b['max_queue']})
    return rows

def summarize(sub):
    return {'n':len(sub),'first_unsafe':sum(x['first_false']>0 for x in sub),
        'final_unsafe':sum(x['final_false']>0 for x in sub),
        'final_admission_improved':sum(x['final_admitted']>x['first_admitted'] for x in sub),
        'final_admission_tied':sum(x['final_admitted']==x['first_admitted'] for x in sub),
        'final_admission_regressed':sum(x['final_admitted']<x['first_admitted'] for x in sub),
        'mean_admission_ratio':sum(x['final_admitted']/max(1,x['first_admitted']) for x in sub)/len(sub),
        'max_return_age':max(x['final_max_age'] for x in sub),
        'filtered_unsafe':sum(x['filtered_false']>0 for x in sub),
        'filtered_vs_final_improved':sum(x['filtered_admitted']>x['final_admitted'] for x in sub),
        'filtered_vs_final_tied':sum(x['filtered_admitted']==x['final_admitted'] for x in sub),
        'filtered_vs_final_regressed':sum(x['filtered_admitted']<x['final_admitted'] for x in sub),
        'mean_filtered_final_ratio':sum(x['filtered_admitted']/max(1,x['final_admitted']) for x in sub)/len(sub)}

def main():
    rows=batch(320,40,940000)+batch(96,12,950000)
    single=[]
    for i in range(32):
        tags,width,steps=make(960000+i,single=True)
        single.append(run(steps,tags,width,'first').metrics==run(steps,tags,width,'final').metrics)
    negative=[]
    for i in range(64):
        tags,width,steps=make(970000+i)
        rng=random.Random(980000+i)
        for s in steps:s['duplicate_final_delta']=rng.randint(1,20) if rng.random()<.12 else None
        negative.append(run(steps,tags,width,'final').metrics['false'])
    report={'discovery':summarize(rows[:320]),'holdout':summarize(rows[320:]),
        'single_beat_identical':sum(single),'single_beat_count':len(single),
        'duplicate_final_unsafe':sum(x>0 for x in negative),
        'duplicate_final_count':len(negative),'surprise_fraction_discovery':.125,
        'surprise_fraction_holdout':.125}
    (HERE/'results.json').write_text(json.dumps({'summary':report,'rows':rows,'single':single,'negative':negative},indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
