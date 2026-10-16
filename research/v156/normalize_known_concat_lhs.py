#!/usr/bin/env python3
"""V156: fail-closed normalization of the sole observed Yosys 0.9 concat-LHS assignment."""
import argparse, hashlib, json, re
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("source",type=Path)
p.add_argument("destination",type=Path)
p.add_argument("--audit",type=Path,required=True)
a=p.parse_args()
s=a.source.read_text()
pattern=r"(?m)^  assign \{ \\lane\[0\]\.pre\.result \[29:23\], \\lane\[0\]\.pre\.result \[21:0\] \} = \{ " + ", ".join([r"\\lane\[0\]\.pre\.result \[30\]"]*7) + r", 22'h000000 \};$"
matches=list(re.finditer(pattern,s))
if len(matches)!=1: raise SystemExit(f"V156 FAIL CLOSED: expected one exact concat-LHS, got {len(matches)}")
replacement="  assign \\lane[0].pre.result [29:23] = { "+", ".join([r"\lane[0].pre.result [30]"]*7)+" };\n  assign \\lane[0].pre.result [21:0] = 22'h000000;"
t=s[:matches[0].start()]+replacement+s[matches[0].end():]
if re.search(r"(?m)^\s*assign\s*\{",t): raise SystemExit("V156 FAIL CLOSED: unsupported concat LHS remains")
for b in (0,1):
    assert sum(b<<i for i in range(23,30)) == sum(b<<i for i in range(23,30))
a.destination.write_text(t)
report={"evidence_class":"syntax normalization only; no STA or RTL equivalence","original_sha256":hashlib.sha256(s.encode()).hexdigest(),"normalized_sha256":hashlib.sha256(t.encode()).hexdigest(),"rewrites":1,"truth_table_cases":2}
a.audit.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
