"""Single-copy, unit-latency synthetic ACK packing capacity test."""
from collections import deque

def run(tags, batch, cycles=8000):
    free=set(range(tags));due={};ack=deque();done=retired=0
    for t in range(cycles):
        if batch and len(ack)>=4:
            n=min(4,len(ack))
            for _ in range(n):free.add(ack.popleft());retired+=1
        elif not batch and ack:
            free.add(ack.popleft());retired+=1
        elif due:
            tag=min(due,key=lambda k:due[k])
            if due[tag]<=t:
                del due[tag];ack.append(tag);done+=1
            elif ack:
                n=min(4,len(ack))
                for _ in range(n):free.add(ack.popleft());retired+=1
        elif ack:
            n=min(4,len(ack))
            for _ in range(n):free.add(ack.popleft());retired+=1
        if free:
            tag=min(free);free.remove(tag);due[tag]=t+1
    assert 0<=done-retired<=tags
    return done/cycles

if __name__=='__main__':
    plain=run(64,False);packed=run(64,True)
    assert .49<plain<.51 and .79<packed<.81
    assert packed/plain>1.5
    print('PASS Vektor-063 ACK bundle synthetic improvement',plain,packed)
