#!/usr/bin/env python3
"""Independent SHA-pinned V296 extracted critical-path locality falsification.

Consumes immutable physical and read-only OpenSTA replay artifacts. OpenSTA
increments include upstream interconnect, not intrinsic cell delay.
D8 pairwise and D4 serial are NOT a matched architecture comparison.
"""
import argparse
import hashlib
import json
import re
from decimal import Decimal as D
from pathlib import Path
from zipfile import ZipFile

E = {
 "D8_pairwise": dict(variant="pairwise", depth=8,
   source_sha="92a84c3923eb62cd506241bcb1d8da06cfcfbd6a13328c8e050b14f301086f4b",
   replay_sha="9ec4107e2d7c3ea1362f0c304280dcc771a738a60e6a5d67fae2118d2ccafbda",
   source_artifact=12769775926, replay_artifact=12776073774,
   start="_22298_", end="_22253_", q="candidate.issue.scheduler.rr1",
   capture="staged_operand_data[3]", setup=D("-0.684592"), hold=D("0.010986"),
   buffer=D("1.372418"), nbuf=40, npins=88),
 "D4_serial_onehot": dict(variant="serial_onehot", depth=4,
   source_sha="edeb136bc054eddf7434119115df198e7d4403c9bd01c0a726df7fb30519755b",
   replay_sha="1ae842da60de4d7a38507188b3e7830ffba57a9fd06881860d9a3eab633a9955",
   source_artifact=12769708334, replay_artifact=12776328412,
   start="_18075_", end="_18073_", q="strongest_serial.issue.scheduler.rr3",
   capture="staged_operand_data[7]", setup=D("-1.316510"), hold=D("0.002572"),
   buffer=D("1.292220"), nbuf=35, npins=92),
}

def sha(b): return hashlib.sha256(b).hexdigest()

def require_zip(path, digest):
    if sha(path.read_bytes()) != digest:
        raise ValueError("Immutable original/replay ZIP SHA-256 mismatch")
    return ZipFile(path)

def section(s, name):
    a,b=("V296_REPLAY_"+name+"_"+x for x in ("BEGIN","END"))
    if s.splitlines().count(a)!=1 or s.splitlines().count(b)!=1:
        raise ValueError("Incomplete or duplicate STA section "+name)
    return s.split(a,1)[1].split(b,1)[0]

def numeric_worst(s):
    m=re.findall(r"^worst slack\s+(-?[0-9.]+)$",s,re.M)
    if len(m)!=1: raise ValueError("Ambiguous extracted worst slack")
    x=D(m[0])
    if not x.is_finite(): raise ValueError("Nonfinite slack")
    return x

def map_flop(netlist, inst):
    m=re.search(r"\bDFF\w+\s+"+re.escape(inst)+r"\s*\((.*?)\);",netlist,re.S)
    if not m: raise ValueError("Cannot map original synthesized flop "+inst)
    p=m.group(1)
    q=re.search(r"\.Q\((.*?)\)",p,re.S)
    d=re.search(r"\.D\((.*?)\)",p,re.S)
    if not q or not d: raise ValueError("Original flop ports missing")
    return {"Q":q[1].strip(),"D":d[1].strip()}

def analyze(case, original_zip, replay_zip):
    c=E[case]
    z=require_zip(original_zip,c["source_sha"])
    r=require_zip(replay_zip,c["replay_sha"])
    x=json.loads(r.read("extracted_paths.json"))
    if (x["verdict"]!="EXTRACTED_PATHS_REPRODUCED_NOT_FEASIBLE" or
        x["artifact_id"]!=c["source_artifact"] or
        x["original_zip_sha256"]!=c["source_sha"] or
        x["depth"]!=c["depth"] or x["variant"]!=c["variant"] or
        x["physical_gate"]!="FAIL" or x["matched_comparison"] is not False or
        x["repair_demonstrated"] is not False or x["gpu_speedup"] is not False):
        raise ValueError("Replay provenance or negative verdict changed")
    s=r.read("replay.log").decode(errors="replace")
    if s.splitlines().count("V296_REPLAY_DONE")!=1:
        raise ValueError("Replay incomplete")
    setup=numeric_worst(section(s,"SETUP_WORST"))
    hold=numeric_worst(section(s,"HOLD_WORST"))
    if setup!=c["setup"] or hold!=c["hold"]:
        raise ValueError("Original extracted timing not exactly reproduced")
    b=section(s,"SETUP_PATHS")
    start=re.findall(r"^Startpoint:\s*(.*)$",b,re.M)
    end=re.findall(r"^Endpoint:\s*(.*)$",b,re.M)
    if (len(start)!=1 or len(end)!=1 or
        not start[0].startswith(c["start"]+" ") or
        not end[0].startswith(c["end"]+" ") or
        "rising edge-triggered flip-flop" not in start[0] or
        "rising edge-triggered flip-flop" not in end[0]):
        raise ValueError("Critical path endpoints not pinned extracted flops")
    if x["setup_path"]["startpoint"]!=start[0] or x["setup_path"]["endpoint"]!=end[0]:
        raise ValueError("Independent JSON/log endpoint mismatch")
    if D(str(x["setup_path"]["slack_ns"]))!=setup:
        raise ValueError("Named path slack differs from extracted worst")
    netlist=z.read(c["variant"]+".v").decode(errors="replace")
    src=map_flop(netlist,c["start"])
    dst=map_flop(netlist,c["end"])
    if c["q"] not in src["Q"] or c["capture"] not in dst["Q"]:
        raise ValueError("Critical RTL-cone identity changed")
    deff=z.read(c["variant"]+".high.cts45.def").decode(errors="replace")
    for inst in (c["start"],c["end"]):
        if not re.search(r"^\s*-\s+"+re.escape(inst)+r"\s+DFF",deff,re.M):
            raise ValueError("Critical flop absent from routed DEF")
    rows=[]
    for line in b.splitlines():
        f=line.split()
        arr=[i for i,v in enumerate(f) if v in ("v","^")]
        if len(arr)!=1: continue
        i=arr[0]
        if i<2 or i+2>=len(f): continue
        try: inc,arrival=D(f[i-2]),D(f[i-1])
        except Exception: continue
        if not inc.is_finite() or not arrival.is_finite():
            raise ValueError("Nonfinite path increment")
        pin,cell=f[i+1],f[i+2].strip("()")
        if "/" in pin: rows.append((inc,arrival,pin,cell))
    if len(rows)!=c["npins"] or x["setup_path"]["path_pin_rows"]!=len(rows):
        raise ValueError("Extracted path length changed")
    launch=[i for i,row in enumerate(rows) if row[2]==c["start"]+"/Q"]
    if len(launch)!=1: raise ValueError("Cannot isolate data path after launch Q")
    data=rows[launch[0]:]
    if data[-1][2]!=c["end"]+"/D": raise ValueError("Capture pin mismatch")
    buffers=[row for row in data if row[3].startswith(("BUF","CLKBUF"))]
    total=sum((row[0] for row in buffers),D(0))
    if len(buffers)!=c["nbuf"] or abs(total-c["buffer"])>D("0.000003"):
        raise ValueError("Original per-pin buffer attribution not reproduced")
    arrivals=re.findall(r"^\s*([0-9.]+)\s+data arrival time$",b,re.M)
    if len(arrivals)!=1 or abs(D(arrivals[0])-data[-1][1])>D("0.000001"):
        raise ValueError("Data arrival does not reconcile")
    deficit=D("0.050")-setup
    if deficit<=0: raise ValueError("Expected physical setup failure missing")
    if total<=deficit:
        status="IMPOSSIBLE_EVEN_IF_ALL_BUFFER_INCREMENT_ELIMINATED"
        minimum_speedup=None
    else:
        status="REQUIRES_BUFFER_ACCELERATION_OVER_BOUNDARY"
        minimum_speedup=str(total/(total-deficit))
    return {
        "case":case,"source_artifact":c["source_artifact"],
        "replay_artifact":c["replay_artifact"],
        "source_zip_sha256":c["source_sha"],"replay_zip_sha256":c["replay_sha"],
        "setup_ns":str(setup),"hold_ns":str(hold),"setup_deficit_ns":str(deficit),
        "critical_start":start[0],"critical_end":end[0],
        "source_rtl_Q":src["Q"],"destination_rtl_Q":dst["Q"],
        "data_path_pin_rows":len(data),"all_path_pin_rows":len(rows),
        "buffer_pin_rows":len(buffers),"buffer_attributed_ns":str(total),
        "twofold_buffer_acceleration_max_saving_ns":str(total/2),
        "buffer_only_repair_status":status,
        "necessary_uniform_buffer_speedup":minimum_speedup,
        "physical_gate":"FAIL","matched_architecture_comparison":False,
        "gpu_throughput_measured":False,
        "path_increments_not_intrinsic_gate_delay":True,
    }

def selftest():
    a=E["D8_pairwise"]; b=E["D4_serial_onehot"]
    assert a["buffer"]/(a["buffer"]-(D(".05")-a["setup"]))>D("2.15")
    assert b["buffer"]<D(".05")-b["setup"]
    assert map_flop("DFFR_X1 _1_ (.CK(clk), .D(n1), .Q(foo[1]), .RN(rst));","_1_")["Q"]=="foo[1]"
    try: map_flop("DFFR_X1 _2_ (.CK(clk), .D(n1), .Q(foo[1]));","_1_")
    except ValueError: pass
    else: raise AssertionError("Missing critical flop accepted")
    print("V296_EXTRACTED_PATH_LOCALITY_SELFTEST_PASS")

def main():
    p=argparse.ArgumentParser()
    for n in ("d8-original","d8-replay","d4-original","d4-replay","output"):
        p.add_argument("--"+n,type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test: selftest()
    if all((a.d8_original,a.d8_replay,a.d4_original,a.d4_replay)):
        out={"source_run":40557136436,"replay_run":40597982594,
             "evidence_tier":"original SHA-locked post-route OpenRCX plus read-only extracted OpenSTA",
             "matched_comparison":False,"physical_gate":"FAIL","holdouts":"SEALED",
             "rows":[analyze("D8_pairwise",a.d8_original,a.d8_replay),
                     analyze("D4_serial_onehot",a.d4_original,a.d4_replay)]}
        s=json.dumps(out,indent=2,sort_keys=True)+"\n"
        if a.output: a.output.write_text(s)
        else: print(s)
    elif not a.self_test: p.error("Provide all four original/replay ZIPs")
if __name__=="__main__": main()
