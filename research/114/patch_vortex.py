#!/usr/bin/env python3
"""Vektor-114: pinned dual-site SimX diagnostic patch.

Records CTA slot allocation/release and per-lane LSU request issue.
No physical-address, retirement, or DRAM-traffic claim is made.
"""
from pathlib import Path
import argparse
import importlib.util
import shutil
import subprocess

PIN = "7fe19369587c087f902c3e2bc2add612aa910a95"
HERE = Path(__file__).resolve().parent

def patch_lsu(src: str) -> str:
    module_path = HERE.parent / "112" / "patch_vortex.py"
    spec = importlib.util.spec_from_file_location("vektor112_patch", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.inject(src)

def patch_cta(src: str) -> str:
    edits = (
        ('#include "cta_dispatcher.h"\n',
         '#include "cta_dispatcher.h"\n#include "vektor_lsu_probe.h"\n'),
        ('    slot_rem_warps_[base] = cta_size_;\n',
         '    slot_rem_warps_[base] = cta_size_;\n'
         '    vektor_lsu_probe::emit({0,0,0,core_->id(),base,0,0,0,\'B\',\'U\'});\n'),
        ('  --slot_rem_warps_[slot];\n',
         '  --slot_rem_warps_[slot];\n'
         '  if (slot_rem_warps_[slot] == 0) {\n'
         '    vektor_lsu_probe::emit({0,0,0,core_->id(),slot,0,0,0,\'E\',\'U\'});\n'
         '  }\n'),
    )
    for before, after in edits:
        if src.count(before) != 1:
            raise ValueError(f"CTA anchor mismatch ({src.count(before)}): {before!r}")
        src = src.replace(before, after)
    return src

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vortex_checkout", type=Path)
    args = ap.parse_args()
    root = args.vortex_checkout.resolve()
    sha = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()
    if sha != PIN:
        raise SystemExit(f"Unpinned Vortex: {sha}; expected {PIN}")
    lsu = root / "sim/simx/lsu_unit.cpp"
    cta = root / "sim/simx/cta_dispatcher.cpp"
    header = root / "sim/simx/vektor_lsu_probe.h"
    if header.exists():
        raise SystemExit("Refusing to overwrite an existing probe header")
    # Prepare both modifications before any write.
    lsu_new = patch_lsu(lsu.read_text())
    cta_new = patch_cta(cta.read_text())
    lsu.write_text(lsu_new)
    cta.write_text(cta_new)
    shutil.copyfile(HERE / "vektor_lsu_probe.h", header)
    print(f"V114 pinned dual-site source patch applied: {sha}")

if __name__ == "__main__":
    main()
