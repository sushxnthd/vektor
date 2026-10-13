#!/usr/bin/env python3
import json,pathlib,re,sys
p=pathlib.Path(sys.argv[1])
out={"evidence_class":"open-library mapped synthesis, no physical STA",
"library_blob":"90e4afb274cfc6514c587c434c77903d554117d1"}
for name in ("control","cutset"):
 s=(p/(name+"_mapped.log")).read_text(errors="replace")
 a=re.findall(r"Chip area for module[^\n]*?:\s*([0-9.]+)",s)
 d=re.findall(r"length\s*=\s*(\d+)",s)
 out[name]={"mapped_area_units":float(a[-1]) if a else None,
            "topological_levels":int(d[-1]) if d else None,
            "log":name+"_mapped.log"}
if out["control"]["mapped_area_units"] and out["cutset"]["mapped_area_units"]:
 out["cutset_area_overhead"]=round(out["cutset"]["mapped_area_units"]/out["control"]["mapped_area_units"]-1,6)
else:out["cutset_area_overhead"]=None
out["timing_verdict"]="pending clock-constrained STA"
out["novelty"]="not established"
print(json.dumps(out,indent=2,sort_keys=True))
