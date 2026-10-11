"""Audit pinned Vortex CTA slot reuse without modifying upstream files."""
from pathlib import Path
import sys
def check(root):
    s=(Path(root)/"sim/simx/cta_dispatcher.cpp").read_text()
    required=[
        "out->cta_id   = cur_slot_;",
        "cur_slot_  = base;",
        "slot_rem_warps_[base] = cta_size_;",
        "--slot_rem_warps_[slot];",
        "if (slot_rem_warps_[base] != 0)"
    ]
    for fragment in required:
        if s.count(fragment)!=1:
            raise ValueError("unexpected pinned Vortex source: "+fragment)
    print("Pinned Vortex CTA slot reuse source audit: PASS")
if __name__=="__main__":check(sys.argv[1])
