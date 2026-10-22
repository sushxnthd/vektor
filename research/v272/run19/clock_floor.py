#!/usr/bin/env python3
"""V272 un-gated DFF clock-pin CV^2 floor, NOT SRAM power or STA."""
import hashlib,json,re,sys
raw=open(sys.argv[1],"rb").read(); s=raw.decode()
m=re.search(r'\bcell\s*\(\s*DFF_X1\s*\)\s*\{',s)
if not m: raise ValueError("DFF_X1 not found")
start=m.end(); depth=1
for i in range(start,len(s)):
    if s[i]=="{": depth+=1
    if s[i]=="}": depth-=1
    if depth==0: break
cell=s[start:i]
p=re.search(r'\bpin\s*\(\s*CK\s*\)\s*\{(.*?)(?=\bpin\s*\(|\Z)',cell,re.S)
if not p: raise ValueError("CK pin not found")
cap=float(re.search(r'\bcapacitance\s*:\s*([\d.]+)',p.group(1)).group(1))
area=float(re.search(r'\barea\s*:\s*([\d.]+)',cell).group(1))
V=1.1; bits=16*32+2*32
pJ=bits*cap*V*V/1000
print(json.dumps({"sha256":hashlib.sha256(raw).hexdigest(),
"library":"Nangate45 typical","cell":"DFF_X1",
"clock_pin_capacitance_fF":cap,"cell_area_um2":area,
"flop_clock_load_bits":bits,"voltage_V":V,
"extra_CV2_pJ_per_core_cycle":pJ,
"extra_clock_pin_mW_at_1GHz":pJ,
"extra_clock_pin_mW_at_2GHz":2*pJ,
"scope":"Un-gated flop-array clock pin only; excludes clock tree, SRAM macro, wires and signoff",
"electrical_gate":"FAIL_UNVERIFIED: no characterized 2x SRAM/clock tree or max-cap/slew STA"},indent=2))
