#!/usr/bin/env python3
"""Read-only, SHA-locked independent DEF/SPEF topology audit of original V296 cap violations."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

EXPECTED = {
    "pairwise": ("06bfdd796801728553fa6c42e853957fb681e52731c73641a9aed403f2905544",
                 -1.047895, -0.036622),
    "serial_onehot": ("5456c370dc860daa67aa61c7a8dc9937291f2b5d89e4e8e51c4ebedf14c6fd1d",
                      -1.859922, -0.019796),
}

def one(pattern, text, label, flags=0):
    hits = list(re.finditer(pattern, text, flags))
    if len(hits) != 1:
        raise ValueError(f"{label}: expected one match, got {len(hits)}")
    return hits[0]

def section(text, a, b):
    x = one("^" + re.escape(a) + "$", text, a, re.M)
    y = one("^" + re.escape(b) + "$", text, b, re.M)
    if y.start() <= x.end():
        raise ValueError("Reversed evidence markers")
    return text[x.end():y.start()]

def audit(path, variant):
    data = path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != EXPECTED[variant][0]:
        raise ValueError("Original artifact ZIP SHA256 mismatch")
    with zipfile.ZipFile(path) as z:
        raw = {key: z.read(f"{variant}.{suffix}").decode() for key, suffix in
               [("log", "high.log"), ("def", "high.cts45.def"),
                ("spef", "high.cts45.spef"), ("netlist", "v")]}
    log, physical, spef, netlist = (raw[k] for k in ("log", "def", "spef", "netlist"))
    if log.splitlines().count("V296_CTS45_DONE") != 1 or log.splitlines().count("V296_CTS45_RC_MULTIPLIER 2.0") != 1:
        raise ValueError("Incomplete or altered physical run")
    m = section(log, "V296_STAGE_BEGIN cts45_extracted", "V296_STAGE_END cts45_extracted")
    setup = float(one(r"^worst slack\s+(-?[0-9.]+)$", m, "setup", re.M).group(1))
    hold = float(one(r"^worst slack\s+(-?[0-9.]+)$",
                     section(log, "V296_CTS45_HOLD_BEGIN", "V296_CTS45_HOLD_END"),
                     "hold", re.M).group(1))
    if abs(setup-EXPECTED[variant][1]) > 1e-6 or abs(hold-EXPECTED[variant][2]) > 1e-6:
        raise ValueError("Original slack altered")
    counts = one(r"^V296_METRIC stage=cts45_extracted area_um2=([0-9.]+) slew=(\d+) cap=(\d+)$",
                 m, "original counts", re.M)
    if (int(counts.group(2)), int(counts.group(3))) != (0,3):
        raise ValueError("Original electrical counts altered")
    v = section(log, "V296_CTS45_CAP_VIOLATORS_BEGIN", "V296_CTS45_CAP_VIOLATORS_END")
    pins = re.findall(r"^(_\d+_)/ZN\s+([0-9.]+)\s+([0-9.]+)\s+(-?[0-9.]+) \(VIOLATED\)$", v, re.M)
    if len(pins) != 3 or len(set(p[0] for p in pins)) != 3:
        raise ValueError("Expected exactly three distinct cap violators")
    mapping = dict(re.findall(r"^\*(\d+)\s+(\S+)$", spef, re.M))
    inverse = {name:key for key,name in mapping.items()}
    if len(inverse) != len(mapping):
        raise ValueError("Ambiguous SPEF name map")
    rows = []
    def placement(cell):
        hit = one(r"^\s*-\s+" + re.escape(cell) +
                  r"\s+(\w+)\s+[^;]*?\+\s+(?:PLACED|FIXED)\s+\(\s*(\d+)\s+(\d+)\s*\)",
                  physical, "DEF placement " + cell, re.M)
        return hit.group(1), int(hit.group(2))/2000, int(hit.group(3))/2000
    for driver, limit, capacitance, slack in pins:
        limit, capacitance, slack = map(float, (limit, capacitance, slack))
        if slack >= 0 or abs(limit-capacitance-slack) > 1e-5:
            raise ValueError("Cap violation arithmetic inconsistent")
        typ, x, y = placement(driver)
        gate = one(r"\b(\w+)\s+" + re.escape(driver) + r"\s*\((.*?)\);",
                   netlist, "mapped driver", re.S)
        net = one(r"\.ZN\(\s*(.*?)\s*\)", gate.group(2), "mapped output").group(1)
        if net not in inverse:
            raise ValueError("Mapped net missing from SPEF")
        record = one(r"^\*D_NET \*" + inverse[net] + r"\s+([0-9.]+)\n(.*?)\*END",
                     spef, "SPEF net", re.M|re.S)
        conn = re.findall(r"^\*I \*(\d+):([^ ]+) ([IO])",
                          record.group(2).split("*CAP")[0], re.M)
        sources = [(mapping[i], pin) for i,pin,d in conn if d=="O"]
        if sources != [(driver, "ZN")]:
            raise ValueError("SPEF driver mismatch")
        sinks = []
        for idx,pin,direction in conn:
            if direction != "I":
                continue
            name = mapping[idx]
            sinktype,sx,sy = placement(name)
            sinks.append({"cell":name, "type":sinktype, "pin":pin,
                          "manhattan_um":round(abs(sx-x)+abs(sy-y),3)})
        if not sinks:
            raise ValueError("SPEF net without sinks")
        rows.append({"driver":driver,"driver_cell":typ,"mapped_cell":gate.group(1),
                     "net":net,"cap_limit_ff":limit,"pin_cap_ff":capacitance,
                     "cap_violation_ff":round(-slack,6),
                     "spef_net_cap_ff":round(float(record.group(1))*1000,6),
                     "sink_count":len(sinks),"sinks":sinks,
                     "max_manhattan_um":max(s["manhattan_um"] for s in sinks)})
    return {"original_zip_sha256":sha,"original_setup_ns":setup,"original_hold_ns":hold,
            "original_area_um2":float(counts.group(1)),"cap_violations":rows}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pairwise-zip",type=Path,required=True)
    ap.add_argument("--serial-zip",type=Path,required=True)
    ap.add_argument("--out",type=Path)
    a=ap.parse_args()
    rows={v:audit(path,v) for v,path in
          [("pairwise",a.pairwise_zip),("serial_onehot",a.serial_zip)]}
    result={"verdict":"ORIGINAL_SPEF_DEF_CAP_TOPOLOGY_VERIFIED",
            "original_run":40156470550,
            "scope":"Original post-route cap topology, not extracted timing-path reconstruction",
            "gpu_speedup":"NOT_ESTABLISHED","rows":rows}
    data=json.dumps(result,indent=2)+"\n"
    if a.out:
        a.out.write_text(data)
    print(data)

if __name__=="__main__":
    main()
