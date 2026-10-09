#!/usr/bin/env python3
"""Vektor-070 finite UID synthetic packet model; terminal accounting is assumed."""
import random, json
from dataclasses import dataclass
@dataclass
class Packet:
    kind: str
    seq: int
    uid: int
    due: int

def simulate(seed, cycles=8000, uid_bits=2, timeout=4, latency=5,
             jitter=4, ack_loss=.15, data_loss=.05, clone_p=.3,
             policy="strong", reset_at=-1):
    rng=random.Random(seed)
    packets=[]; active=None; next_seq=0; next_send=0
    issued=seen=ack_seen=False; fenced_until=0
    deliveries=sends=retries=retirements=false_data=false_ack=resets=0
    reset_wait=False
    for t in range(cycles):
        if t==reset_at:
            active=None; reset_wait=True; resets+=1
        due=[p for p in packets if p.due<=t]
        packets=[p for p in packets if p.due>t]
        rng.shuffle(due)
        for p in due:
            if rng.random()<(ack_loss if p.kind=="ACK" else data_loss):
                continue
            if active is None or p.uid!=active%(1<<uid_bits):
                continue
            if p.seq!=active:
                if p.kind=="DATA": false_data+=1
                else: false_ack+=1
            if p.kind=="DATA":
                if not seen:
                    seen=True; deliveries+=1
                packets.append(Packet("ACK",p.seq,p.uid,t+rng.randint(latency,latency+jitter)))
            elif issued:
                ack_seen=True
        if reset_wait and not packets:
            reset_wait=False; fenced_until=t+1
        if active is None and not reset_wait and t>=fenced_until:
            if policy=="strong" and packets: continue
            active=next_seq; next_seq+=1; next_send=t
            issued=seen=ack_seen=False
        if active is None: continue
        if not ack_seen and t>=next_send:
            if issued: retries+=1
            issued=True; sends+=1
            uid=active%(1<<uid_bits)
            packets.append(Packet("DATA",active,uid,t+rng.randint(latency,latency+jitter)))
            if rng.random()<clone_p:
                packets.append(Packet("DATA",active,uid,t+rng.randint(latency,latency+jitter+latency)))
            next_send=t+timeout
        if ack_seen and (policy=="early" or not packets):
            retirements+=1; active=None; fenced_until=t+1
    return dict(seed=seed,cycles=cycles,uid_bits=uid_bits,timeout=timeout,
                latency=latency,jitter=jitter,ack_loss=ack_loss,data_loss=data_loss,
                clone_p=clone_p,policy=policy,reset_at=reset_at,
                retirements=retirements,deliveries=deliveries,sends=sends,
                retries=retries,false_data=false_data,false_ack=false_ack,
                resets=resets,pending_packets=len(packets))
if __name__=="__main__":
    runs=[]
    for policy in ("strong","early"):
        for uid_bits in (1,2,3):
            for timeout,latency in ((2,3),(4,5),(8,7),(16,10)):
                for seed in (3,11,29,47):
                    runs.append(simulate(seed,uid_bits=uid_bits,timeout=timeout,
                                         latency=latency,policy=policy,
                                         jitter=latency,clone_p=.65))
    extra=[simulate(s+1000,uid_bits=1+s%3,timeout=1+s%13,latency=1+s%11,
                    jitter=s%8,clone_p=.1+.075*(s%10),
                    ack_loss=.1+.04*(s%5),data_loss=.02,
                    reset_at=3000) for s in range(12)]
    strong=[r for r in runs if r["policy"]=="strong"]+extra
    early=[r for r in runs if r["policy"]=="early"]
    assert all(not(r["false_data"] or r["false_ack"]) for r in strong)
    assert any(r["false_data"] or r["false_ack"] for r in early)
    summary=dict(structured=len(runs),exploratory=len(extra),
                 strong_retirements=sum(r["retirements"] for r in strong),
                 strong_false_data=sum(r["false_data"] for r in strong),
                 strong_false_ack=sum(r["false_ack"] for r in strong),
                 early_false_data=sum(r["false_data"] for r in early),
                 early_false_ack=sum(r["false_ack"] for r in early),
                 early_unsafe_runs=sum(bool(r["false_data"] or r["false_ack"]) for r in early))
    print(json.dumps(summary,indent=2))
