#!/usr/bin/env python3
"""V115: fail-closed probe emitter + pinned-source + actual-trace audit.

Scope: source-pinned SimX issue-stage addresses and CTA lifecycle.
Never treat these records as post-MMU addresses, retirement, DRAM traffic,
or measured GPU performance. No third-party runtime dependency.
"""
import argparse
import csv
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "113"))
from lifetime import parse, hazard

HEADER = ROOT / "research" / "113" / "probe.h"
PIN = "7fe19369587c087f902c3e2bc2add612aa910a95"

HARNESS = r'''
#include "research/113/probe.h"
int main() {
  using namespace vektor_lsu_probe;
  emit({0,0,0,1,0,0,0,0,'B','U'});
  emit({11,100,4096,1,0,0,0,4,'S','S'});
  emit({0,0,0,1,0,0,0,0,'E','U'});
  emit({0,0,0,1,0,0,0,0,'B','U'});
  emit({12,104,4096,1,0,0,0,4,'L','S'});
  emit({0,0,0,1,0,0,0,0,'E','U'});
}
'''

def rows(path):
    with open(path, newline="") as f:
        return list(csv.reader(f))

def emitter_smoke():
    assert HEADER.exists()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        src, exe, trace = tmp / "smoke.cpp", tmp / "smoke", tmp / "trace.csv"
        src.write_text(HARNESS)
        subprocess.run(["g++", "-std=c++17", "-Wall", "-Wextra", "-Werror",
                        "-I", str(ROOT), str(src), "-o", str(exe)], check=True)
        env = dict(os.environ, VEKTOR_LSU_TRACE=str(trace))
        subprocess.run([str(exe)], env=env, check=True)
        recs = rows(trace)
        assert len(recs) == 6 and all(len(r) == 13 for r in recs)
        assert [int(r[0]) for r in recs] == list(range(6))
        with open(trace) as f:
            ev = parse(f)
        assert len(ev) == 2 and ev[0].cta != ev[1].cta
        assert not hazard(ev[0], ev[1])  # shared allocations differ by generation
        # Counterfactual: global memory retains alias across generations.
        global_rows = [r.copy() for r in recs]
        global_rows[1][10] = global_rows[4][10] = "G"
        path = tmp / "global.csv"
        with open(path, "w", newline="") as f:
            csv.writer(f).writerows(global_rows)
        with open(path) as f:
            a, b = parse(f)
        assert hazard(a, b)
        # Negative control: duplicated allocation must be rejected.
        bad = [r.copy() for r in recs]
        bad[2][7] = "B"
        bad[2][12] = "cta_allocate"
        path = tmp / "bad.csv"
        with open(path, "w", newline="") as f:
            csv.writer(f).writerows(bad)
        try:
            with open(path) as f:
                parse(f)
        except ValueError:
            pass
        else:
            raise AssertionError("malformed lifecycle accepted")
    print("V115 compiled C++ emitter, identity, alias and malformed-trace controls: PASS")

def audit_patched(path):
    root = Path(path)
    commit = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"],
                                     text=True).strip()
    assert commit == PIN, (commit, PIN)
    lsu = (root / "sim/simx/lsu_unit.cpp").read_text()
    cta = (root / "sim/simx/cta_dispatcher.cpp").read_text()
    header = (root / "sim/simx/vektor_lsu_probe.h").read_text()
    assert lsu.count("vektor_lsu_probe::emit(") == 2
    assert cta.count("vektor_lsu_probe::emit(") == 2
    assert lsu.count('#include "vektor_lsu_probe.h"') == 1
    assert cta.count('#include "vektor_lsu_probe.h"') == 1
    assert "VEKTOR_LSU_TRACE" in header
    assert "lsu_req.uuid = trace->uuid;" in lsu
    assert "core_->lmem_switch(b)->ReqIn.send(lsu_req);" in lsu
    assert "slot_rem_warps_[slot] == 0" in cta
    print("V115 pinned source patch and four logging sites: PASS; NOT a simulator build")

def audit_trace(path):
    path = Path(path)
    assert path.exists() and path.stat().st_size, "missing/empty actual trace"
    recs = rows(path)
    assert len(recs) >= 4
    assert all(len(r) == 13 for r in recs)
    assert [int(r[0]) for r in recs] == list(range(len(recs)))
    with path.open() as f:
        events = parse(f)
    assert events, "no LSU issue events"
    allocations = sum(r[7] == "B" for r in recs)
    releases = sum(r[7] == "E" for r in recs)
    assert allocations == releases and allocations > 0
    ops = {k: sum(r[7] == k for r in recs) for k in "LSAF"}
    print(f"V115 actual SimX issue/lifecycle trace: PASS; events={len(recs)}, "
          f"allocations={allocations}, releases={releases}, LSU={len(events)}, ops={ops}")
    print("Evidence stage: simulator issue only; not physical traffic/retirement/performance")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--audit-patched", metavar="VORTEX_CHECKOUT")
    p.add_argument("--trace", metavar="CSV")
    args = p.parse_args()
    if args.audit_patched:
        audit_patched(args.audit_patched)
    elif args.trace:
        audit_trace(args.trace)
    else:
        emitter_smoke()
