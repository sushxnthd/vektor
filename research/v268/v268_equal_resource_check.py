#!/usr/bin/env python3
"""Exact RTL structural equal-resource control check. Not RTL simulation."""
from pathlib import Path
import re,json
p=Path(__file__).parent
src=(p/'v268_sector_rf.sv').read_text()
ctrl=src.replace('module v268_sector_rf','module v268_equal_sector_gated_control',1)
(p/'v268_equal_sector_gated_control.sv').write_text(ctrl)
norm=lambda s:re.sub(r'\b(v268_sector_rf|v268_equal_sector_gated_control)\b','SAME',re.sub(r'//[^\n]*','',s))
assert norm(src)==norm(ctrl)
print(json.dumps({'result':'RETIRE','equal_resource_control':'conventional active-mask sector-gated RF','normalized_RTL_identical':True,'incremental_advantage':0,'physical_PPA':'not measured','holdouts':'unopened'},indent=2))
