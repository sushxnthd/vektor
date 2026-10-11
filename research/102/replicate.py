"""Cross-check discovery grid against independent C++ implementation."""
import json,subprocess,tempfile
from pathlib import Path
from sweep import discovery
from joint_cost import run
def main():
    root=Path(__file__).parent
    with tempfile.TemporaryDirectory() as td:
        exe=Path(td)/'replica'
        subprocess.run(['g++','-O2','-std=c++17',str(root/'replicate.cpp'),'-o',str(exe)],check=True)
        configs=discovery()
        data=''.join(f'{c.pattern} {c.length} {c.rf_ports} {c.migration_bw} {c.memory_stride} {c.locality}\n' for c in configs)
        p=subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True)
        lines=p.stdout.splitlines()
        assert len(lines)==len(configs)
        for i,(c,line) in enumerate(zip(configs,lines)):
            got=list(map(int,line.split()))
            expected=run(c)['totals']
            want=[expected[x] for x in ['ipdom','dwf','heuristic','oracle']]
            assert got==want,(i,c,got,want)
        print(json.dumps({'independent_cpp_matches':len(lines),'mismatches':0}))
if __name__=='__main__':main()
