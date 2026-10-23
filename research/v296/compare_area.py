#!/usr/bin/env python3
"""Nangate45 matched area gate; no electrical STA inference."""
import json,re,sys,pathlib
def area(path):
    s=pathlib.Path(path).read_text()
    m=re.findall(r"Chip area for (?:top )?module[^:\n]*:\s*([0-9.]+)",s)
    if not m: raise RuntimeError("Missing characterized area: "+path)
    return float(m[-1])
orig,opt,pair=map(area,sys.argv[1:4])
best=min(orig,opt)
out={"original_um2":orig,"optimized_um2":opt,"pairwise_um2":pair,
     "best_control_um2":best,"ratio":pair/best,
     "area_gate":"FAIL" if pair>best else "PASS",
     "electrical_STA":"NOT_RUN","workload_holdouts":"SEALED"}
print(json.dumps(out,indent=2))
pathlib.Path("build/v296/area.json").write_text(json.dumps(out,indent=2)+"\n")
if pair>best: sys.exit("V296 RETIRE: area exceeds best matched control")
