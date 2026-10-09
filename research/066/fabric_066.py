#!/usr/bin/env python3
"""Vektor-066 synthetic bidirectional DATA/ACK replay experiment; not GPU data.
All physical DATA copies are counted at their final replication point.
Receiver UID history is unbounded; IDs never wrap in this finite simulation.
"""
import heapq, random, json, argparse

def simulate(seed=11,tags=4,cycles=2500,data_loss=.1,ack_loss=.1,
             replay=.5,delay=8,timeout=6,identity="full"):
    assert identity in ("full","tag")
    rng=random.Random(seed)
    active={} # tag -> {uid, outstanding, last_send, ack}
    seen=set(); q=[]; serial=0; uid=0
    stat=dict(completed=0,issued=0,false_ack=0,stale_ack=0,
              duplicate_data=0,unique_data=0,acks=0,data=0)
    def send(now,kind,tag,ident,loss):
        nonlocal serial
        for _ in range(1+(rng.random()<replay)):
            serial+=1
            heapq.heappush(q,(now+rng.randint(1,delay),serial,kind,
                              tag,ident,rng.random()>=loss))
            if kind=="data": active[tag]["out"]+=1
    for now in range(cycles):
        while q and q[0][0]<=now:
            _,_,kind,tag,ident,delivered=heapq.heappop(q)
            tx=active.get(tag)
            if kind=="data":
                if tx and tx["uid"]==ident:
                    tx["out"]-=1
                    assert tx["out"]>=0
                else: raise AssertionError("DATA survived strong quiescence")
                if delivered:
                    stat["data"]+=1
                    if ident in seen: stat["duplicate_data"]+=1
                    else: seen.add(ident);stat["unique_data"]+=1
                    send(now,"ack",tag,ident,ack_loss)
            elif delivered:
                stat["acks"]+=1
                if not tx: stat["stale_ack"]+=1
                elif identity=="tag" or tx["uid"]==ident:
                    if tx["uid"]!=ident: stat["false_ack"]+=1
                    tx["ack"]=True
                else: stat["stale_ack"]+=1
        for tag,tx in list(active.items()):
            if tx["ack"] and tx["out"]==0:
                del active[tag];stat["completed"]+=1
        for tag in range(tags):
            if tag not in active:
                uid+=1;active[tag]=dict(uid=uid,out=0,last=-10**9,ack=False)
                stat["issued"]+=1
            tx=active[tag]
            if not tx["ack"] and now-tx["last"]>=timeout:
                tx["last"]=now
                send(now,"data",tag,tx["uid"],data_loss)
        assert len(active)<=tags
    stat.update(rate=stat["completed"]/cycles,active=len(active),
                pending=len(q))
    if identity=="full": assert stat["false_ack"]==0
    return stat

def main():
    # Preregistered: full UID zero false ACK credits; tag-only unsafe under
    # delayed replay even if DATA replicas are drained before reclamation.
    cases=[]
    for seed in (11,23,37,53):
      for tags in (1,2,4,8):
       for delay in (2,8,24):
        for loss in (0.,.2,.5):
         for replay in (0.,.5):
          r=simulate(seed,tags,2500,loss,loss,replay,delay)
          cases.append(dict(seed=seed,tags=tags,delay=delay,
                            loss=loss,replay=replay,**r))
    assert len(cases)==288 and all(r["false_ack"]==0 for r in cases)
    rng=random.Random(66066)
    probes=[]
    for _ in range(36):
        probes.append(simulate(seed=rng.randrange(10**7),
           tags=rng.randint(1,12),cycles=2500,
           data_loss=rng.random()*.8,ack_loss=rng.random()*.8,
           replay=rng.random(),delay=rng.randint(1,40),
           timeout=rng.randint(1,16)))
    unsafe=[simulate(seed=s,tags=t,cycles=4000,data_loss=.1,
       ack_loss=.1,replay=1.,delay=24,timeout=4,identity="tag")
       for s in (1,2,3,4) for t in (1,2,4,8)]
    assert sum(x["false_ack"] for x in unsafe)>0
    no_ack=simulate(seed=1,tags=2,cycles=1000,data_loss=0.,
                    ack_loss=1.,replay=0.,delay=2,timeout=4)
    assert no_ack["completed"]==0
    out=dict(structured_runs=len(cases),exploratory_runs=len(probes),
       tag_only_cases=len(unsafe),tag_only_false_credits=sum(
       x["false_ack"] for x in unsafe),full_false_credits=sum(
       x["false_ack"] for x in cases+probes),
       no_ack_completions=no_ack["completed"])
    print(json.dumps(out,indent=2))
    return out

if __name__=="__main__":
    main()
