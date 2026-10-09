"""Vektor-063: deterministic event-model CI."""
from collections import deque
import heapq, random

def run(seed, tags, p, policy, cycles=8000):
    rng=random.Random(seed)
    jobs=[(rng.randint(1,4),16 if rng.random()<p else None) for _ in range(30000)]
    free=set(range(tags));live={};events=[];data=deque();acks=deque()
    issued=done=retired=data_sent=ack_sent=duplicates=0
    for t in range(cycles):
        while events and events[0][0]<=t:
            _,_,tag,owner=heapq.heappop(events);data.append((tag,owner))
        def send_data():
            nonlocal done,data_sent,duplicates
            if not data:return False
            tag,owner=data.popleft();data_sent+=1
            tr=live[tag];assert tr[0]==owner
            tr[1]-=1
            if not tr[2]:tr[2]=True;done+=1
            else:duplicates+=1
            if tr[1]==0:acks.append((tag,owner))
            return True
        def send_ack():
            nonlocal retired,ack_sent
            if not acks:return False
            tag,owner=acks.popleft();assert live[tag]==[owner,0,True]
            del live[tag];free.add(tag);retired+=1;ack_sent+=1
            return True
        if policy=='dedicated':send_data();send_ack()
        elif policy=='ack_first':
            if not send_ack():send_data()
        else:
            if not send_data():send_ack()
        if free:
            tag=min(free);free.remove(tag);issued+=1
            first,gap=jobs[issued-1];live[tag]=[issued,2 if gap else 1,False]
            heapq.heappush(events,(t+first,issued*2,tag,issued))
            if gap:heapq.heappush(events,(t+first+gap,issued*2+1,tag,issued))
    assert done>=retired and done-retired<=tags
    assert data_sent==done+duplicates
    assert ack_sent==retired
    if policy!='dedicated':assert data_sent+ack_sent<=cycles
    return done/cycles

if __name__=='__main__':
    count=0
    for seed in (7,19,31):
      for tags in (8,64):
       for p in (0,.1,.4):
        x={mode:run(seed,tags,p,mode) for mode in ('dedicated','ack_first','data_first')}
        assert x['dedicated']>=x['ack_first']-0.01
        if tags==64 and p==0:
            assert x['dedicated']>.99 and .49<x['ack_first']<.51
        count+=3
    print('PASS Vektor-063 deterministic egress simulations:',count)
