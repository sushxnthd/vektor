#!/usr/bin/env python3
"""Extract comparable mapped cell area from Yosys JSON + Nangate45 liberty.
This is a synthesis area proxy, NOT routed PPA or switching power.
"""
import json,re,sys,pathlib
lib=pathlib.Path(sys.argv[1]).read_text()
areas={}
for m in re.finditer(r'\bcell\s*\(\s*([^)]+)\s*\)\s*\{',lib):
    start=m.end()
    nxt=re.search(r'\n\s*cell\s*\(',lib[start:])
    block=lib[start:start+nxt.start()] if nxt else lib[start:]
    a=re.search(r'\barea\s*:\s*([\d.]+)',block)
    if a: areas[m.group(1).strip().strip('"')]=float(a.group(1))
res={}
for fn in sys.argv[2:]:
    obj=json.loads(pathlib.Path(fn).read_text())
    modules=obj['modules']
    top=next((k for k,v in modules.items() if v.get('attributes',{}).get('top') in (1,'00000000000000000000000000000001')),None)
    if top is None: top=pathlib.Path(fn).stem.replace('_mapped','')
    cells=modules[top]['cells']
    missing=sorted({v['type'] for v in cells.values()}-set(areas))
    if missing: raise RuntimeError(f'Unmapped/unpriced cells in {fn}: {missing[:12]}')
    counts={}
    for c in cells.values(): counts[c['type']]=counts.get(c['type'],0)+1
    res[top]={'area_um2':round(sum(areas[t]*n for t,n in counts.items()),6),
              'cells':len(cells),'cell_counts':counts}
print(json.dumps(res,indent=2,sort_keys=True))
if 'v287_lane_control' in res and 'v287_lane_fuse_phys' in res:
    b=res['v287_lane_control']['area_um2']
    c=res['v287_lane_fuse_phys']['area_um2']
    print('V287_AREA_RATIO=%.6f'%(c/b))
