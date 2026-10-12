#!/usr/bin/env python3
"""V125 preregistered deterministic RTL differential vectors.

Three independent paths: V124 Python interpreter, V124 C++ interpreter,
new per-step Python model, plus Icarus RTL (in CI). Never equate agreement
with timing closure, memory support, or GPU-level performance.
"""
import argparse
import json
import random
import subprocess
import tempfile
from pathlib import Path
from reference_v124 import run as prior_python

ROOT=Path(__file__).resolve().parent
OP={'laneid':0,'imm':1,'add':2,'mul':3,'xor':4,'iflt':5,
    'else':6,'endif':7,'ballot':8,'reduce_add':9}
MASK=(1<<32)-1

class Model:
    def __init__(self, mask):
        self.mask=mask
        self.r=[[0]*32 for _ in range(16)]
        self.frames=[]
    def step(self, op, a):
        old=self.mask
        if op=='iflt':
            cond=sum(1<<i for i in range(32) if old>>i&1 and self.r[a[0]][i]<self.r[a[1]][i])
            self.frames.append([old,cond,False]); self.mask=cond;return
        if op=='else':
            p,c,seen=self.frames[-1];assert not seen
            self.frames[-1][2]=True;self.mask=p&~c;return
        if op=='endif':
            self.mask=self.frames.pop()[0];return
        if op=='ballot':
            v=sum(1<<i for i in range(32) if old>>i&1 and self.r[a[1]][i]!=0)
        elif op=='reduce_add':
            v=sum(self.r[a[1]][i] for i in range(32) if old>>i&1)&MASK
        for i in range(32):
            if not (old>>i&1):continue
            if op=='laneid':self.r[a[0]][i]=i
            elif op=='imm':self.r[a[0]][i]=a[1]&MASK
            elif op=='add':self.r[a[0]][i]=(self.r[a[1]][i]+self.r[a[2]][i])&MASK
            elif op=='mul':self.r[a[0]][i]=(self.r[a[1]][i]*self.r[a[2]][i])&MASK
            elif op=='xor':self.r[a[0]][i]=self.r[a[1]][i]^self.r[a[2]][i]
            elif op in ('ballot','reduce_add'):self.r[a[0]][i]=v

def programs():
    # Locked before execution: 224 configurations, 28 minimally-guided (12.5%).
    # Seeds 125000..125223; fixed arithmetic/predication opcode distribution.
    for n in range(224):
        rng=random.Random(125000+n)
        surprise=n%8==0
        mask=rng.getrandbits(32) if surprise else rng.choice([MASK,0x55555555,0xaaaaaaaa,0x0000ffff,0x00ff00ff])
        p=[('laneid',[0]),('imm',[1,rng.choice([0,1,7,16,31,0xffffffff])])]
        frames=[]
        nops=rng.randint(9,35) if surprise else rng.randint(10,26)
        for _ in range(nops):
            choice=rng.random()
            if choice<0.17 and len(frames)<3:
                a,b=rng.randrange(16),rng.randrange(16)
                p.append(('iflt',[a,b]));frames.append(False)
            elif choice<0.25 and frames and not frames[-1]:
                p.append(('else',[]));frames[-1]=True
            elif choice<0.34 and frames:
                p.append(('endif',[]));frames.pop()
            else:
                op=rng.choice(['laneid','imm','add','mul','xor','ballot','reduce_add'])
                rd=rng.randrange(16)
                if op=='laneid':a=[rd]
                elif op=='imm':a=[rd,rng.choice([0,1,0xffffffff,0x80000000,rng.getrandbits(32)])]
                elif op in ('ballot','reduce_add'):a=[rd,rng.randrange(16)]
                else:a=[rd,rng.randrange(16),rng.randrange(16)]
                p.append((op,a))
        while frames:
            p.append(('endif',[]));frames.pop()
        yield n,mask,p,surprise

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--replica',default='')
    args=parser.parse_args()
    counts={'programs':0,'instructions':0,'rtl_state_checks':0,'surprise_programs':0,
            'python_model_matches':0,'cpp_matches':0,'mismatches':0}
    out=[]
    for n,mask,program,surprise in programs():
        counts['programs']+=1
        counts['surprise_programs']+=int(surprise)
        m=Model(mask)
        out.append(f'R {mask:08x}')
        # Validate empty-stack fault path before first instruction.
        out.extend(['E 6','E 7','E 15'])
        for index,(op,a) in enumerate(program):
            x=a+[0]*(3-len(a))
            rd,rs1,rs2=0,0,0
            imm=0
            if op=='laneid':rd=a[0]
            elif op=='imm':rd=a[0];imm=a[1]
            elif op in ('add','mul','xor'):rd,rs1,rs2=a
            elif op=='iflt':rs1,rs2=a
            elif op in ('ballot','reduce_add'):rd,rs1=a
            out.append(f'I {OP[op]} {rd} {rs1} {rs2} {imm:08x}')
            m.step(op,a)
            out.append(f'C {m.mask:08x} {len(m.frames)}')
            # Sample 4 registers/lane positions each step, all 512 at end.
            if index!=len(program)-1:
                for r,l in [(0,0),(1,31),(rd,0),(rd,31)]:
                    out.append(f'D {r} {l} {m.r[r][l]:08x}')
            counts['instructions']+=1
        assert not m.frames
        for r in range(16):
            for l in range(32):out.append(f'D {r} {l} {m.r[r][l]:08x}')
        source='\n'.join(op+' '+' '.join(map(str,a)) for op,a in program)+'\n'
        prior=prior_python(source,[0],mask)
        if prior['registers']!=m.r:
            counts['mismatches']+=1
            raise AssertionError(f'V124 Python mismatch seed={125000+n}')
        counts['python_model_matches']+=1
        if args.replica:
            with tempfile.TemporaryDirectory() as tmp:
                code=Path(tmp)/'p.kpx'; mem=Path(tmp)/'m.txt'
                code.write_text(source);mem.write_text('0\n')
                result=subprocess.run([args.replica,str(code),str(mem),str(mask)],check=True,capture_output=True,text=True)
                if json.loads(result.stdout)['registers']!=m.r:
                    counts['mismatches']+=1
                    raise AssertionError(f'V124 C++ mismatch seed={125000+n}')
            counts['cpp_matches']+=1
    counts['rtl_state_checks']=sum(1 for line in out if line.startswith(('C ','D ','E ')))
    (ROOT/'vectors.txt').write_text('\n'.join(out)+'\n')
    (ROOT/'local_results.json').write_text(json.dumps(counts,indent=2)+'\n')
    print(json.dumps(counts,sort_keys=True))
if __name__=='__main__':main()
