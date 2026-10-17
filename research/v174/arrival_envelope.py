#!/usr/bin/env python3
"""Conditional V156 input-arrival envelope; not a new STA run."""
import json,sys
from pathlib import Path
s=json.loads(Path(sys.argv[1]).read_text())
c=s["candidates"]["control"]
t=s["candidates"]["cutset"]
assert "flip-flop" in c["worst_path_startpoint"]
assert "input port" in t["worst_path_startpoint"]
dc=c["constrained_period_minus_worst_slack_ns"]
dt=t["constrained_period_minus_worst_slack_ns"]
ac,at=7558.39,7821.46
for d in (0.05,0.5,1,2,3,4,5):
    x=d-0.05
    cut=dt+x
    lo,hi=dc,dc+x
    print(json.dumps({"delay_ns":d,"cutset_delay_ns":round(cut,6),
      "control_interval_ns":[lo,round(hi,6)],
      "timing_gain_interval_pct":[round(100*(1-cut/lo),6),round(100*(1-cut/hi),6)],
      "area_delay_gain_interval_pct":[round(100*(1-at*cut/(ac*lo)),6),round(100*(1-at*cut/(ac*hi)),6)]}))
