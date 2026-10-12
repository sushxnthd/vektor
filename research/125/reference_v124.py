"""KPX-0: deliberately small, deterministic Wave32 integer ISA reference.

Semantics: 32 unsigned lanes, uint32 wrap, per-lane registers, structured
mask stack, 32-bit word addressed memory, ascending-lane conflicting stores.
NOT a GPU ISA implementation, cycle model, IEEE floating-point datapath, or RTL.
"""
from dataclasses import dataclass, asdict
import json

WAVE=32
MASK=(1<<32)-1
REGS=16
OPS={"laneid":2,"imm":3,"add":4,"mul":4,"xor":4,"load":4,"store":4,
     "iflt":3,"else":1,"endif":1,"ballot":3,"reduce_add":3}

@dataclass
class Stats:
    instructions:int=0
    active_lanes:int=0
    memory_requests:int=0
    unique_lines:int=0
    unique_sectors:int=0
    divergent_regions:int=0


def parse(src):
    program=[]
    stack=[]
    for lineno,line in enumerate(src.splitlines(),1):
        words=line.split('#',1)[0].split()
        if not words: continue
        op=words[0]
        if op not in OPS or len(words)!=OPS[op]:
            raise ValueError(f"line {lineno}: unknown opcode/arity: {line}")
        args=[]
        for x in words[1:]:
            try: args.append(int(x,0))
            except ValueError: raise ValueError(f"line {lineno}: invalid operand {x}") from None
        regs = {"laneid":[0],"imm":[0],"add":[0,1,2],"mul":[0,1,2],
                "xor":[0,1,2],"load":[0,1],"store":[0,1],
                "iflt":[0,1],"ballot":[0,1],"reduce_add":[0,1]}.get(op,[])
        if any(args[i]<0 or args[i]>=REGS for i in regs):
            raise ValueError(f"line {lineno}: invalid register")
        if op=="iflt":stack.append(False)
        elif op=="else":
            if not stack or stack[-1]:raise ValueError(f"line {lineno}: unmatched else")
            stack[-1]=True
        elif op=="endif":
            if not stack:raise ValueError(f"line {lineno}: unmatched endif")
            stack.pop()
        program.append((op,args))
    if stack:raise ValueError("unclosed iflt")
    return program


def run(src,memory,initial_mask=MASK):
    if initial_mask<0 or initial_mask>MASK:raise ValueError("invalid active mask")
    p=parse(src)
    reg=[[0]*WAVE for _ in range(REGS)]
    mem=[x&MASK for x in memory]
    mask=initial_mask
    stack=[]
    stats=Stats()
    for op,a in p:
        if op=="iflt":
            parent=mask
            cond=sum((1<<i) for i in range(WAVE)
                     if (parent>>i)&1 and reg[a[0]][i]<reg[a[1]][i])
            if cond!=0 and cond!=parent:stats.divergent_regions+=1
            stack.append((parent,cond,False))
            mask=cond
            continue
        if op=="else":
            parent,cond,seen=stack[-1]
            stack[-1]=(parent,cond,True)
            mask=parent & ~cond
            continue
        if op=="endif":
            parent,_,_=stack.pop()
            mask=parent
            continue
        stats.instructions+=1
        stats.active_lanes+=mask.bit_count()
        if op in ("load","store"):
            addresses=[(i,(reg[a[1]][i]+a[2])&MASK) for i in range(WAVE) if (mask>>i)&1]
            if any(addr>=len(mem) for _,addr in addresses):raise IndexError("KPX memory OOB")
            stats.memory_requests+=len(addresses)
            stats.unique_lines+=len({addr//32 for _,addr in addresses})
            stats.unique_sectors+=len({addr//8 for _,addr in addresses})
            for i,addr in addresses:
                if op=="load":reg[a[0]][i]=mem[addr]
                else:mem[addr]=reg[a[0]][i]
            continue
        if op=="ballot":
            ballot=sum((1<<i) for i in range(WAVE) if (mask>>i)&1 and reg[a[1]][i]!=0)
            for i in range(WAVE):
                if (mask>>i)&1:reg[a[0]][i]=ballot
            continue
        if op=="reduce_add":
            total=sum(reg[a[1]][i] for i in range(WAVE) if (mask>>i)&1)&MASK
            for i in range(WAVE):
                if (mask>>i)&1:reg[a[0]][i]=total
            continue
        for i in range(WAVE):
            if not (mask>>i)&1:continue
            if op=="laneid":reg[a[0]][i]=i
            elif op=="imm":reg[a[0]][i]=a[1]&MASK
            elif op=="add":reg[a[0]][i]=(reg[a[1]][i]+reg[a[2]][i])&MASK
            elif op=="mul":reg[a[0]][i]=(reg[a[1]][i]*reg[a[2]][i])&MASK
            elif op=="xor":reg[a[0]][i]=reg[a[1]][i]^reg[a[2]][i]
    return {"memory":mem,"registers":reg,"stats":asdict(stats)}


def compile_kernel(kind, stride=1, limit=16, scale=3):
    """Small structured frontend lowering 3 kernels to KPX-0 text ISA.
    All addresses are 32-bit *word* addresses, not byte addresses.
    """
    if not (1<=stride<=64 and 0<=limit<=32 and 0<=scale<=MASK):
        raise ValueError("invalid kernel parameters")
    base=f"laneid 0\nimm 1 {stride}\nmul 2 0 1\n"
    if kind=="gather":
        return base+"load 3 2 0\nimm 4 256\nadd 5 0 4\nstore 3 5 0\n"
    if kind=="masked_affine":
        return (base+f"imm 6 {limit}\niflt 0 6\nload 3 2 0\n"
                +f"imm 4 {scale}\nmul 3 3 4\nadd 3 3 0\n"
                +"imm 5 256\nadd 5 5 0\nstore 3 5 0\nelse\nimm 3 0\n"
                +"imm 5 256\nadd 5 5 0\nstore 3 5 0\nendif\n")
    if kind=="reduction":
        return base+"load 3 2 0\nreduce_add 4 3\nimm 5 256\nstore 4 5 0\n"
    raise ValueError(kind)
