#!/usr/bin/env python3
import json,re,pathlib
logs={}
for mode in ('original','balanced'):
    s=pathlib.Path(f'build/v152/{mode}.yosys.log').read_text()
    counts=re.findall(r'\b(?:Number of cells|number of cells):?\s+(\d+)',s,re.I)
    depths=re.findall(r'length=(\d+)',s)
    logs[mode]={'generic_cells':int(counts[-1]) if counts else None,'generic_path_levels':int(depths[-1]) if depths else None}
print(json.dumps({'evidence_class':'generic_yosys_synthesis_not_physical_ppa','synthesis':logs,'claim':'comparison only; no mapped timing or workload throughput inference'},indent=2))
