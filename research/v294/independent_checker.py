#!/usr/bin/env python3
"""Independent V294 bank-capacity oracle. No physical performance claim."""
import itertools, json, random

def fits(used, pair):
    x,y=pair
    return used[x]+(x==y)<=1 and used[y]+(x==y)<=1

def schedule(slots, lookahead):
    used=[0]*16
    result=[]
    for idx,(p,a) in enumerate(slots):
        pf=p is not None and fits(used,p)
        af=a is not None and fits(used,a)
        if not (pf or af):
            result.append(None)
            continue
        choose_alt=not pf
        if pf and af and lookahead:
            future=[b for future_p,_ in slots[idx+1:] if future_p is not None for b in future_p]
            choose_alt=sum(b in a for b in future)<sum(b in p for b in future)
        selected=a if choose_alt else p
        for b in selected: used[b]+=1
        result.append("a" if choose_alt else "p")
    assert max(used)<=2
    return result

def exact_max(slots):
    best=0
    for choices in itertools.product((None,"p","a"),repeat=4):
        used=[0]*16
        count=0
        for (p,a),choice in zip(slots,choices):
            if choice is None: continue
            pair=p if choice=="p" else a
            if pair is None or not fits(used,pair): break
            for b in pair: used[b]+=1
            count+=1
        else: best=max(best,count)
    return best

def count(v):
    return sum(x is not None for x in v)

def main():
    positive=[((0,1),(4,5)),((0,1),None),((0,1),None),((8,9),None)]
    no_win=[((0,1),None),((2,3),None),((4,5),None),((6,7),None)]
    assert (count(schedule(positive,False)),count(schedule(positive,True)))==(3,4)
    assert (count(schedule(no_win,False)),count(schedule(no_win,True)))==(4,4)
    rng=random.Random(294)
    sums={"baseline":0,"lookahead":0,"optimal":0,"wins":0,"losses":0,"ties":0}
    for _ in range(2000):
        slots=[]
        for i in range(4):
            p=(rng.randrange(8),rng.randrange(8)) if rng.random()<.9 else None
            a=(rng.randrange(8),rng.randrange(8)) if rng.random()<.75 else None
            slots.append((p,a))
        base=count(schedule(slots,False))
        look=count(schedule(slots,True))
        opt=exact_max(slots)
        assert look<=opt and base<=opt
        sums["baseline"]+=base
        sums["lookahead"]+=look
        sums["optimal"]+=opt
        sums["wins"]+=look>base
        sums["losses"]+=look<base
        sums["ties"]+=look==base
    print(json.dumps({"evidence":"E0 oracle only",
      "frozen_positive":{"control":3,"lookahead":4},
      "frozen_no_win":{"control":4,"lookahead":4},
      "random_cases":2000,"aggregate":sums},indent=2))
if __name__=="__main__": main()
