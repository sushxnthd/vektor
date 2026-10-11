"""Self-contained repository smoke test; full V108 differential suite in package."""
from dataclasses import dataclass
from pathlib import Path
import random,subprocess
from validator import strict_valid

@dataclass(frozen=True)
class Event:
    tid:int;pc:int;epoch:int;op:str;addr:int;value:int=0

def legacy_order_valid(events,waves):
    from validator import dependencies
    pos={i:t for t,w in enumerate(waves) for i in w}
    if len(pos)!=len(events):return False
    if any(pos[p]>=pos[i] for i,ps in enumerate(dependencies(events)) for p in ps):return False
    bounds={}
    for i,e in enumerate(events):
        if e.epoch not in bounds:bounds[e.epoch]=[len(waves),-1]
        bounds[e.epoch][0]=min(bounds[e.epoch][0],pos[i])
        bounds[e.epoch][1]=max(bounds[e.epoch][1],pos[i])
    eps=sorted(bounds)
    return all(bounds[a][1]<bounds[b][0] for a,b in zip(eps,eps[1:]))

def main():
    atomic=[Event(0,0,0,'A',4096,1),Event(32,0,0,'L',8192)]
    assert legacy_order_valid(atomic,[[0],[0,1]])
    assert not strict_valid(atomic,[[0],[0,1]])
    rng=random.Random(1092026);cases=[]
    for _ in range(216):
        events=[Event(i,0,0,'L',4096+32*i) for i in range(rng.randrange(1,32))]
        base=[list(range(len(events)))];dup=[base[0][:], [base[0][0]]]
        empty=[[],base[0][:]]
        cases.extend([(events,base),(events,dup),(events,empty)])
    lines=[str(len(cases))]
    for events,waves in cases:
        lines.append(f'{len(events)} {len(waves)} 32')
        lines.extend(f'{e.tid} {e.pc} {e.epoch} {e.op} {e.addr} {e.value}' for e in events)
        lines.extend(' '.join(map(str,[len(w)]+w)) for w in waves)
    src=Path(__file__).with_name('replica.cpp')
    binary=Path(__file__).with_name('replica')
    subprocess.run(['g++','-std=c++17','-O2',str(src),'-o',str(binary)],check=True)
    out=subprocess.run([str(binary)],input='\n'.join(lines)+'\n',text=True,capture_output=True,check=True)
    cpp=[x=='1' for x in out.stdout.splitlines()]
    py=[strict_valid(e,w) for e,w in cases]
    assert cpp==py and len(py)==648
    assert sum(py)==216
    print('V109 repository smoke test passed: 648 independent C++/Python comparisons; 216 valid controls')

if __name__=='__main__':main()
