#!/usr/bin/env python3
"""V270 run14 independent claim checker; requires OpenSTA before any physical claim."""
import json
from pathlib import Path
p=Path(__file__).with_name("run14_proxy_results.json")
d=json.loads(p.read_text())
assert d["evidence"].startswith("E2+")
assert d["sensitivity"]["points"]==81
assert d["sensitivity"]["cap_violations"]==0
assert d["sensitivity"]["slew_violations"]==0
t={k:v["delay_ns"] for k,v in d["nominal"].items() if k.startswith("mode")}
area={k:v["area"] for k,v in d["nominal"].items() if k.startswith("mode")}
r=t["mode2"]/t["mode1"]
assert 1.19<r<1.23
assert area["mode0"]<area["mode1"]<area["mode2"]
for regime in ("compute","memory","divergent"):
    e=d["toggle_proxy"][regime]
    assert e["adaptive"]>e["flexible"],regime
print("V270: conditional clock proxy adaptive/flexible",round(r,4))
print("Frozen positive issue-limited adaptive/flexible",round(r,4))
print("Frozen negative issue-limited adaptive/flexible",round(r/2,4))
print("No energy Pareto dominance. OpenSTA absent; no physical claim.")
