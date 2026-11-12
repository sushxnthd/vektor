"""Independent V317 persistent-queue challenge: FIFO and rotating age controls.
No RTL, electrical, or GPU throughput claim. Run: python research/v317/rtl/queue_age_controls_20261107.py
"""
import random
SEEDS=(11,23,37)
CYCLES=20000
BANKS=3

def arrivals(seed,hot):
    rng=random.Random(seed)
    for _ in range(CYCLES):
        batch=[]
        for _ in range(3):
            if rng.random()<.68:
                a=0 if rng.random()<hot else rng.randrange(BANKS)
                b=0 if rng.random()<hot else rng.randrange(BANKS)
                batch.append((a,b))
        yield batch

def simulate(seed,hot,policy):
    queue=[]; completed=0; wait=0; max_age=0; arrived=0
    for cycle,batch in enumerate(arrivals(seed,hot)):
        arrived+=len(batch)
        queue.extend((a,b,cycle) for a,b in batch)
        head=queue[:4]
        order=list(range(len(head)))
        if policy=='minimum_contention':
            order.sort(key=lambda i:(sum((head[i][0] in (x[0],x[1]))+(head[i][1] in (x[0],x[1])) for x in head),i))
        elif policy=='weighted_contention':
            loads=[sum((a==j)+(b==j) for a,b,_ in head) for j in range(BANKS)]
            order.sort(key=lambda i:(loads[head[i][0]]+loads[head[i][1]],i))
        elif policy=='fifo':
            pass
        elif policy=='rotating':
            order=order[cycle%len(order):]+order[:cycle%len(order)] if order else []
        else: raise ValueError(policy)
        used=[0]*BANKS; selected=[]
        for i in order:
            a,b,_=head[i]
            demand=[int(a==j)+int(b==j) for j in range(BANKS)]
            if all(used[j]+demand[j]<=2 for j in range(BANKS)):
                selected.append(i)
                used=[used[j]+demand[j] for j in range(BANKS)]
        for i in sorted(selected,reverse=True):
            age=cycle-queue[i][2]
            wait+=age;max_age=max(max_age,age)
            queue.pop(i);completed+=1
    assert completed+len(queue)==arrived
    return completed,len(queue),wait/completed,max_age

if __name__=='__main__':
    print('hot,seed,policy,completed,backlog,mean_wait,max_completed_age')
    for hot in (0.,.3,.7):
        for seed in SEEDS:
            for policy in ('fifo','rotating','minimum_contention','weighted_contention'):
                result=simulate(seed,hot,policy)
                print(f'{hot},{seed},{policy},'+','.join(map(str,result)))
