#!/usr/bin/env python3
"""Matched Nangate45 mapped-area gate. This is NOT electrical STA."""
import json,re,sys,pathlib
def area(name):
    s=pathlib.Path(name).read_text()
    m=re.findall(r"Chip area for (?:top )?module[^:\n]*:\s*([0-9.]+)",s)
    if not m: raise RuntimeError("No characterized area: "+name)
    return float(m[-1])
original,optimized,parallel=map(area,sys.argv[1:4])
best=min(original,optimized)
result=dict(evidence="Nangate45 standard-cell mapped area, not STA",
    original_um2=original,optimized_um2=optimized,parallel_um2=parallel,
    best_control_um2=best,ratio=parallel/best,
    area_gate="FAIL" if parallel>best else "PASS",
    electrical_gate="NOT_TESTED",timing_gate="NOT_TESTED")
print(json.dumps(result,indent=2))
pathlib.Path("build/v295/area.json").write_text(json.dumps(result,indent=2)+"\n")
if parallel>best: sys.exit("RETIRE V295: fails matched mapped-area gate")
