"""Fail-closed optional source-pinned Vortex SimX LSU issue probe.
Does not assert that patched Vortex builds or executes.
"""
from pathlib import Path
import argparse,subprocess,shutil
PIN="7fe19369587c087f902c3e2bc2add612aa910a95"
HERE=Path(__file__).resolve().parent
INC='#include "lsu_unit.h"\n'
REQ='\t\tlsu_req.uuid = trace->uuid;\n\n\t\t// send memory request\n'
FENCE='\t\tstate.fence.engage(trace);\n\t\tDT(3, this->name() << " fence-lock: " << *trace);\n'
REQ_NEW='''\t\tlsu_req.uuid = trace->uuid;
        // Optional Vektor diagnostic: logs only issued virtual addresses.
        for (uint32_t vektor_i=0; vektor_i<beat_n; ++vektor_i) {
          if (!lsu_req.mask.test(vektor_i)) continue;
          const auto& vektor_e=state.addr_list.at(t0+vektor_i);
          const auto vektor_type=get_addr_type(vektor_e.addr);
          const char vektor_class=(vektor_type==AddrType::Shared)?'S'
                                  :(vektor_type==AddrType::IO)?'I':'G';
          vektor_lsu_probe::emit({trace->uuid,static_cast<uint64_t>(trace->PC),
              vektor_e.addr,trace->cid,trace->cta_id,trace->wid,
              vektor_e.tid,vektor_e.size,
              is_amo?'A':(is_write?'S':'L'),vektor_class});
        }

\t\t// send memory request
'''
FENCE_NEW='''\t\tstate.fence.engage(trace);
        vektor_lsu_probe::emit({trace->uuid,static_cast<uint64_t>(trace->PC),
            0,trace->cid,trace->cta_id,trace->wid,0,0,'F','U'});
\t\tDT(3, this->name() << " fence-lock: " << *trace);
'''
def inject(source):
    for old,new in ((INC,INC+'#include "vektor_lsu_probe.h"\n'),
                    (REQ,REQ_NEW),(FENCE,FENCE_NEW)):
        if source.count(old)!=1:raise ValueError("Upstream source anchor mismatch: "+repr(old[:55]))
        source=source.replace(old,new)
    return source
def main():
    p=argparse.ArgumentParser()
    p.add_argument("vortex_checkout",type=Path)
    args=p.parse_args()
    root=args.vortex_checkout
    sha=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    if sha!=PIN:raise SystemExit("Refusing unpinned Vortex checkout: "+sha)
    path=root/"sim/simx/lsu_unit.cpp"
    modified=inject(path.read_text())
    path.write_text(modified)
    shutil.copyfile(HERE/"vektor_lsu_probe.h",root/"sim/simx/vektor_lsu_probe.h")
    print("Source patched; simulator build/run NOT yet verified")
if __name__=="__main__":main()
