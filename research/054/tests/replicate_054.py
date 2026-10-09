#!/usr/bin/env python3
"""Independent packed-state interpretation of the RTL interface, not RTL simulation."""
import sys

class Replica:
    def __init__(self,dedup):
        self.dedup=dedup
        self.live=[False,False]
        self.tags=[0,0]
        self.regs=[[0]*3 for _ in range(2)]
        self.sent=[[False]*3 for _ in range(2)]
        self.received=[[False]*3 for _ in range(2)]
        self.data=[[0]*3 for _ in range(2)]
        self.rr=0
        self.error=0

    def tick(self,row):
        rst,iv,it,ir,rdy,rv,rt,op,reg,val,cr,er,eq,eqt,eop,eqg,ec,ect,ecd,eerr=row
        incoming=[(ir>>(8*j))&255 for j in range(3)]
        free=next((s for s in range(2) if not self.live[s]),-1)
        issue_ready=int(free!=-1 and all(not self.live[s] or self.tags[s]!=it for s in range(2)))
        request=None
        for slot in (self.rr,1-self.rr):
            if not self.live[slot]:continue
            for o in range(3):
                if self.sent[slot][o]:continue
                if self.dedup and self.regs[slot][o] in self.regs[slot][:o]:continue
                request=(slot,o,self.tags[slot],self.regs[slot][o]);break
            if request:break
        complete=next((s for s in range(2) if self.live[s] and all(self.received[s])),None)
        comp_data=sum(self.data[complete][j]<<(32*j) for j in range(3)) if complete is not None else 0
        actual=[issue_ready,int(request is not None),request[2] if request else 0,request[1] if request else 0,
                request[3] if request else 0,int(complete is not None),self.tags[complete] if complete is not None else 0,
                comp_data,self.error]
        expected=[er,eq,eqt,eop,eqg,ec,ect,ecd,eerr]
        if actual!=expected:
            raise AssertionError(f'actual={actual}, expected={expected}')
        if complete is not None and cr:self.live[complete]=False
        if iv and issue_ready:
            self.live[free]=True;self.tags[free]=it;self.regs[free]=incoming
            self.sent[free]=[False]*3;self.received[free]=[False]*3;self.data[free]=[0]*3
        if request and rdy:
            s,o,_,_=request
            self.sent[s][o]=True;self.rr=1-s
        if rv:
            matches=[s for s in range(2) if self.live[s] and self.tags[s]==rt]
            s=matches[0] if matches else -1
            if s<0 or op>=3 or self.regs[s][op]!=reg or not self.sent[s][op] or self.received[s][op]:
                self.error=1
            else:
                for j in range(3):
                    if (self.regs[s][j]==reg if self.dedup else j==op):
                        self.received[s][j]=True;self.data[s][j]=val

def run(path,dedup):
    r=Replica(dedup);count=0
    for line in open(path):
        fields=line.split()
        if len(fields)!=20:raise ValueError((count,len(fields)))
        h={2,3,6,8,9,13,15,17,18}
        row=[int(x,16 if i in h else 10) for i,x in enumerate(fields)]
        try:r.tick(row)
        except Exception as e:raise AssertionError(f'cycle {count}: {e}') from e
        count+=1
    return count

if __name__=='__main__':
    n=run(sys.argv[1],int(sys.argv[2]));print('PASS independent packed-state model',n,'cycles')
