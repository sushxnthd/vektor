"""V147: executable Wave32 collector -> exact FP32 FMA -> scoreboard/writeback model.
Evidence class: software cycle simulation; this is NOT an RTL or timing claim.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import random
import struct
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(path, name):
    spec=importlib.util.spec_from_file_location(name, path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

Collector=load(ROOT/'research/v146/verification/collector_oracle.py','v146_collector').Collector
fma_bits=load(ROOT/'research/v147/fma_oracle.py','v147_fma').fma_bits
LANES=32
REGS=64

@dataclass(frozen=True)
class Inst:
    dst:int
    src:tuple[int,int,int]
    mask:int

def bits(x):
    return struct.unpack('<I',struct.pack('<f',x))[0]

def generate(seed,kind,count):
    r=random.Random(seed)
    special=[0,0x80000000,1,0x007fffff,0x7f800000,0xff800000,0x7fc00000]
    regs=[[r.choice(special) if r.random()<.035 else bits(r.uniform(-2,2)) for _ in range(LANES)] for _ in range(REGS)]
    instructions=[]
    for i in range(count):
        if kind=='chain':
            dst=0; src=(0,1+i%4,2+i%4)
        elif kind=='bankhot':
            dst=16*(i%3)+(i%2);src=(0,16,32) if i%2 else (1,17,33)
        elif kind=='bankhot_indep':
            dst=48+(i%16);src=(0,16,32) if i%2 else (1,17,33)
        elif kind=='independent':
            dst=16+(i%16);src=(i%16,(i+7)%16,(i+11)%16)
        elif kind=='divergent':
            dst=i%16;src=(dst,(dst+17)%64,(dst+31)%64)
        else:
            dst=r.randrange(64);src=tuple(r.randrange(64) for _ in range(3))
            if i%5==0:src=(src[0],src[0],src[2])
        mask=((1<<LANES)-1) if kind!='divergent' else sum(1<<k for k in range(LANES) if r.random()<.28)
        instructions.append(Inst(dst,src,mask))
    return regs,instructions

def reference(initial,instructions):
    regs=[x[:] for x in initial]
    expected=[]
    for ins in instructions:
        src=[regs[s][:] for s in ins.src]
        result=regs[ins.dst][:]
        for lane in range(LANES):
            if (ins.mask>>lane)&1:
                result[lane]=fma_bits(src[0][lane],src[1][lane],src[2][lane])[0]
        regs[ins.dst]=result
        expected.append(result[:])
    return regs,expected

def run(seed=147,kind='mixed',count=80,ports=2,rf_latency=1,fma_latency=3,stall_prob=.08,bank_map='low'):
    assert ports in (1,2) and rf_latency>=1 and fma_latency>=1 and bank_map in ('low','xor')
    def bank(reg):return (reg&15) if bank_map=='low' else ((reg^(reg>>4))&15)
    initial,instructions=generate(seed,kind,count)
    final_ref,expected=reference(initial,instructions)
    regs=[x[:] for x in initial]
    collector=Collector()
    pending_dst={}
    execq=[]
    inflight={}
    issue_idx=0
    retired=0
    rng=random.Random(seed ^ 0xA57E)
    counters=dict(seed=seed,kind=kind,count=count,ports=ports,rf_latency=rf_latency,
                  fma_latency=fma_latency,bank_map=bank_map,cycles=0,retired=0,rf_responses=0,
                  duplicate_sources=0,wb_overlap_cycles=0,bank_conflicts=0,
                  dispatch_stalls=0,enqueue_stalls=0,scoreboard_waw_stalls=0,
                  rf_wait_cycles=0,fp32_lanes=0,fp32_mismatches=0)
    responses=[]
    max_cycles=100000
    for cycle in range(max_cycles):
        wb=None
        if execq and execq[0][0]<=cycle and rng.random()>=stall_prob:
            due,tag,result=execq.pop(0)
            idx,ins=inflight.pop(tag)
            if result!=expected[idx]:
                counters['fp32_mismatches']+=sum(x!=y for x,y in zip(result,expected[idx]))
                raise AssertionError(('FMA mismatch',kind,seed,idx,result,expected[idx]))
            regs[ins.dst]=result[:]
            del pending_dst[ins.dst]
            wb=(ins.dst,tuple(result))
            retired+=1
            counters['retired']+=1
        if retired==count:
            counters['cycles']=cycle+1
            if regs!=final_ref:raise AssertionError(('final state',kind,seed))
            return counters
        eligible=[p for p in responses if p[0]<=cycle]
        used=[]
        for p in eligible:
            if len(used)>=ports:break
            if bank(p[1]) not in {bank(x[1]) for x in used}:used.append(p)
            else:counters['bank_conflicts']+=1
        while len(used)<2:used.append(None)
        rsp=[(bool(p),p[1] if p else 0,bank(p[1]) if p else 0,p[2] if p else (0,)*LANES) for p in used]
        enq=None
        if issue_idx<count and not collector.active:
            ins=instructions[issue_idx]
            if ins.dst in pending_dst:
                counters['scoreboard_waw_stalls']+=1
            else:
                enq=(issue_idx,ins.src)
        dispatch_ready=len(execq)<2 and rng.random()>=stall_prob
        enq_ready,dispatch,accepted,payload=collector.step(enq,rsp,wb,dispatch_ready)
        for p,accept in zip(used,accepted):
            if p and accept:
                responses.remove(p)
                counters['rf_responses']+=1
        if enq_ready and enq is not None:
            idx=issue_idx
            pending_dst[instructions[idx].dst]=idx
            inflight[idx]=(idx,instructions[idx])
            counters['duplicate_sources']+=len(set(instructions[idx].src))<3
            issue_idx+=1
        elif issue_idx<count:counters['enqueue_stalls']+=1
        if dispatch and not dispatch_ready:counters['dispatch_stalls']+=1
        if wb and collector.active:counters['wb_overlap_cycles']+=1
        if dispatch and dispatch_ready:
            tag,operands=payload
            idx,ins=inflight[tag]
            out=regs[ins.dst][:]
            for lane in range(LANES):
                if (ins.mask>>lane)&1:
                    out[lane]=fma_bits(*(operands[s][lane] for s in range(3)))[0]
                    counters['fp32_lanes']+=1
            execq.append((cycle+fma_latency,tag,out))
        if collector.active:
            outstanding={p[1] for p in responses}
            needed={r for r,v in zip(collector.regs,collector.vals) if v is None}
            available=[r for r in sorted(needed) if r not in outstanding and (r not in pending_dst or pending_dst[r]==collector.tag)]
            if not available:counters['rf_wait_cycles']+=1
            for reg in available:
                responses.append((cycle+rf_latency,reg,tuple(regs[reg])))
        else:
            responses=[]
    raise TimeoutError((kind,seed,retired,count,counters))

def suite(holdout=False):
    data=[]
    seeds=(42,314159,8675309,20261014,20261015) if holdout else (147,5090,20261013)
    count=128 if holdout else 64
    for kind in ('chain','independent','bankhot','bankhot_indep','divergent','mixed'):
        for seed in seeds:
            for ports in (1,2):
                for mapping in ('low','xor'):
                    data.append(run(seed,kind,count,ports,bank_map=mapping))
    assert all(x['retired']==x['count'] and x['fp32_mismatches']==0 for x in data)
    return data

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--suite',action='store_true')
    parser.add_argument('--holdout',action='store_true')
    args=parser.parse_args()
    print(json.dumps(suite(args.holdout) if (args.suite or args.holdout) else run(),indent=2))
