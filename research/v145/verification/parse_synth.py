#!/usr/bin/env python3
"""Machine-readable generic Yosys cell/depth comparison, NOT PPA."""
import json, pathlib, re
root=pathlib.Path("build/v145")
def read(name):
    s=(root/name).read_text()
    cells=re.findall(r"Number of cells:\s+(\d+)",s)
    paths=re.findall(r"Longest topological path in .*?\(length=(\d+)\)",s)
    if not cells or not paths:raise RuntimeError("missing synthesis metrics: "+name)
    return dict(generic_cells=int(cells[-1]),generic_logic_depth=int(paths[-1]))
flex=read("synth_flexible.log")
fixed=read("synth_fixed.log")
out={"evidence_class":"Yosys generic synthesis; not mapped area, delay, power or silicon",
     "tool":"Yosys 0.33 on ubuntu-latest",
     "baseline_flexible":flex,"candidate_fixed":fixed,
     "fixed_over_flexible_cells":round(fixed["generic_cells"]/flex["generic_cells"],6),
     "fixed_over_flexible_depth":round(fixed["generic_logic_depth"]/flex["generic_logic_depth"],6),
     "same_router_interfaces":True,
     "upstream_bank_to_bus_fabric_included":False}
(root/"synth_metrics.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
