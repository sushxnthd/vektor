#!/usr/bin/env python3
"""SHA-locked original V296 critical-path delay-budget checker (Python stdlib).
Usage: python3 research/v296/path_delay_decomposition.py pairwise.zip serial.zip
The OpenSTA increments include upstream net effects; they are not intrinsic cell delays.
"""
import argparse
from collections import defaultdict
from decimal import Decimal
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile

D=Decimal
EXPECTED={
 "pairwise":("239a648829c41f5cd0229ec1ca6663463ca2a253d9186321bb476869223e640e","_15189_","_15164_",D("-1.047895")),
 "serial_onehot":("d755641eba65a4b89c36f1226ae23e55ce647b390dc910e649d157360d538815","_15350_","_15342_",D("-1.859922")),
}
ROW=re.compile(r"^\s*([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)\s+(?:[\^v]\s+)?(\S+)\s+\(([^()]+)\)\s*$")
def extract(pattern, block):
    return [D(x) for x in re.findall(pattern,block,re.M)]
def classify(pin,cell):
    inst,_,suffix=pin.partition("/")
    if suffix=="CK":return "clock_pin"
    if suffix=="Q" and cell.startswith("DFF"):return "clock_to_q"
    if suffix=="D" and cell.startswith("DFF"):return "capture_pin"
    if inst.startswith(("rebuffer","max_cap","max_length","load_slew","wire")):
        assert cell.startswith(("BUF","CLKBUF")), (pin,cell)
        return "buffer"
    if cell.startswith(("BUF","CLKBUF")):return "buffer"
    return "functional"
def check(path,variant):
    sha,start,end,expected_slack=EXPECTED[variant]
    assert hashlib.sha256(path.read_bytes()).hexdigest()==sha,"original ZIP SHA mismatch"
    with ZipFile(path) as z:
        log=z.read(variant+".high.log").decode()
        audit=json.loads(z.read(variant+".tile.audit.json"))
    assert log.count("V296_IN_SITU_SETUP_PATHS_BEGIN")==1
    block=log.split("V296_IN_SITU_SETUP_PATHS_BEGIN",1)[1].split("V296_IN_SITU_SETUP_PATHS_END",1)[0]
    assert "Startpoint: "+start+" " in block and "Endpoint: "+end+" " in block
    assert "Path Type: max" in block
    clk=extract(r"^\s*([+-]?\d+\.\d+)\s+[+-]?\d+\.\d+\s+clock network delay \(propagated\)\s*$",block)
    assert len(clk)==2
    rows=[]
    for line in block.splitlines():
        m=ROW.match(line)
        if m:
            inc,cum,pin,cell=m.groups()
            rows.append((D(inc),D(cum),pin,classify(pin,cell)))
    assert len(rows)>=20 and rows[0][3]=="clock_pin" and rows[-1][3]=="capture_pin"
    running=clk[0]
    sums=defaultdict(lambda:D(0))
    counts=defaultdict(int)
    for inc,cum,pin,kind in rows:
        running+=inc
        assert abs(running-cum)<=D("0.000015"),("bad cumulative arrival",pin)
        sums[kind]+=inc
        counts[kind]+=1
    arrival=extract(r"^\s*([+-]?\d+\.\d+)\s+data arrival time\s*$",block)
    required=extract(r"^\s*([+-]?\d+\.\d+)\s+data required time\s*$",block)
    slack=extract(r"^\s*([+-]?\d+\.\d+)\s+slack \(VIOLATED\)\s*$",block)
    assert arrival and required and len(slack)==1
    assert abs(running-arrival[0])<=D("0.000015")
    assert required[-1]-arrival[0]==slack[0]
    assert slack[0]==expected_slack==D(str(audit["final"]["setup_ns"]))
    assert audit["final"]["cap"]==3 and audit["final"]["hold_ns"]<0
    buffer=sums["buffer"]
    nonbuffer=sums["functional"]+sums["clock_to_q"]+sums["capture_pin"]
    assert abs(clk[0]+buffer+nonbuffer-arrival[0])<=D("0.000015")
    deficit=D("0.050000")-slack[0]
    chains=[]; chain=[]
    for inc,_,pin,kind in rows:
        if kind=="buffer":chain.append((inc,pin))
        elif chain:chains.append(chain);chain=[]
    if chain:chains.append(chain)
    chains.sort(key=lambda x:sum((v[0] for v in x),D(0)),reverse=True)
    return {
      "variant":variant,"artifact_sha256":sha,"startpoint":start,"endpoint":end,
      "setup_slack_ns":float(slack[0]),"target_slack_ns":0.05,
      "required_recovery_ns":float(deficit),
      "arrival_ns":float(arrival[0]),"required_ns":float(required[-1]),
      "launch_clock_ns":float(clk[0]),"clock_to_q_ns":float(sums["clock_to_q"]),
      "functional_attributed_ns":float(sums["functional"]),
      "buffer_attributed_ns":float(buffer),
      "nonbuffer_attributed_ns":float(nonbuffer),
      "functional_cell_count":counts["functional"],"buffer_count":counts["buffer"],
      "largest_buffer_chain":{"count":len(chains[0]),"delay_ns":float(sum((v[0] for v in chains[0]),D(0))),"start":chains[0][0][1],"end":chains[0][-1][1]},
      "hypothetical_fractional_buffer_saving":{
        f:{"buffer_saving_ns":float(D(f)*buffer),
           "additional_nonbuffer_saving_required_ns":float(max(D(0),deficit-D(f)*buffer))}
        for f in ("0","0.25","0.5","0.75","1")}
    }
def main():
    assert classify("wire42/Z","CLKBUF_X2")=="buffer"
    assert classify("_42_/ZN","OAI33_X1")=="functional"
    try:classify("wire42/Z","NAND2_X1")
    except AssertionError:pass
    else:raise AssertionError("buffer identity guard failed")
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("pairwise_zip",type=Path);p.add_argument("serial_onehot_zip",type=Path)
    a=p.parse_args()
    pair=check(a.pairwise_zip,"pairwise"); serial=check(a.serial_onehot_zip,"serial_onehot")
    print(json.dumps({
      "evidence_tier":"SHA-verified original post-route extracted OpenSTA worst setup path per design",
      "warning":"STA cell-output increments include upstream interconnect; not intrinsic gate/wire split, not a physical repair or signoff",
      "pairwise":pair,"serial_onehot":serial,
      "paired":{"slack_lead_ns":pair["setup_slack_ns"]-serial["setup_slack_ns"],
        "buffer_attributed_difference_ns":serial["buffer_attributed_ns"]-pair["buffer_attributed_ns"],
        "nonbuffer_attributed_difference_ns":serial["nonbuffer_attributed_ns"]-pair["nonbuffer_attributed_ns"]}
    },indent=2,sort_keys=True))
if __name__=="__main__":main()
