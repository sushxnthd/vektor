from collections import deque

def run(tags, batch, cycles=8000):
    free=set(range(tags)); due={}; ack=deque(); done=retired=0
    for t in range(cycles):
        if batch and len(ack)>=4:
            for _ in range(4): free.add(ack.popleft());retired+=1
        elif not batch and ack:
            free.add(ack.popleft());retired+=1
        elif due:
            tag=min(due,key=lambda k:due[k])
            if due[tag]<=t:
                del due[tag];ack.append(tag);done+=1
            elif ack:
                while ack: free.add(ack.popleft());retired+=1
        elif ack:
            while ack: free.add(ack.popleft());retired+=1
        if free:
            tag=min(free);free.remove(tag);due[tag]=t+1
        assert 0<=done-retired<=tags
    return done/cycles

if __name__=='__main__':
    print('Synthetic ACK tests',run(64,False),run(64,True))
