#!/usr/bin/env python3
"""Independent audit of hosted V296 RTL and mapped combinational synthesis.

python3 research/v296/v296_parallel_threshold_mapped_audit.py artifact.zip --expected-zip-sha256 SHA
NOT STA, extracted delay, power or GPU throughput.
"""
import argparse
import hashlib
import json
import re
import sys
import zipfile

EXPECTED_LIB = "8d540a4d4cf6d09d27c87ad067857a9c0c2eeb023ab7a56e058cd3113db4e9b1"
TOPS = ("v296_pairwise_arbiter", "v296_pairwise_parallel_threshold", "v296_onehot_scaling")

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def mapped(log, top):
    require("check -assert" in log, f"{top}: missing structural check")
    areas = re.findall(r"Chip area for module '\\" + re.escape(top) + r"':\s*([0-9.]+)", log)
    paths = re.findall(r"Longest topological path in " + re.escape(top) + r" \(length=(\d+)\):", log)
    cells = re.findall(r"^\s*Number of cells:\s*(\d+)\s*$", log, re.M)
    require(len(areas) == 1 and len(paths) == 1 and len(cells) >= 2,
            f"{top}: missing or ambiguous mapped statistics")
    require("Executing ABC pass" in log or "ABC RESULTS" in log, f"{top}: no ABC mapping")
    return {"area_um2":float(areas[0]), "mapped_cells":int(cells[-1]),
            "longest_topological_path_edges":int(paths[0])}

def run():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("artifact_zip")
    p.add_argument("--expected-zip-sha256")
    a = p.parse_args()
    data = open(a.artifact_zip,"rb").read()
    digest = hashlib.sha256(data).hexdigest()
    if a.expected_zip_sha256:
        require(digest == a.expected_zip_sha256, "artifact checksum mismatch")
    with zipfile.ZipFile(a.artifact_zip) as z:
        names = set(z.namelist())
        required = {f"{top}.synth.log" for top in TOPS} | {
            "library.sha256", "nangate.lib", "rtl.log", "math_oracle.log", "yosys.version"}
        require(required <= names, f"missing artifact members: {sorted(required-names)}")
        lib = hashlib.sha256(z.read("nangate.lib")).hexdigest()
        require(lib == EXPECTED_LIB, "frozen Liberty checksum mismatch")
        require(z.read("library.sha256").decode().split()[0] == lib, "library manifest mismatch")
        require("V296_PARALLEL_THRESHOLD_EQUIVALENCE_PASS checks=164976" in z.read("rtl.log").decode(),
                "RTL equivalence marker absent")
        require("V296_INDEPENDENT_MATH_ORACLE_PASS cases=164976" in z.read("math_oracle.log").decode(),
                "independent oracle marker absent")
        result = {top:mapped(z.read(f"{top}.synth.log").decode(),top) for top in TOPS}
        version = z.read("yosys.version").decode().strip()
    orig,alt,ctrl = (result[t] for t in TOPS)
    require(alt["area_um2"] < orig["area_um2"], "area reduction not reproduced")
    require(alt["longest_topological_path_edges"] > orig["longest_topological_path_edges"],
            "depth regression not reproduced")
    print(json.dumps({
        "evidence_tier":"Yosys/ABC Nangate45 mapped combinational proxies; NOT STA/post-route",
        "artifact_sha256":digest, "liberty_sha256":lib, "yosys_version":version,
        "rtl_checks":164976, "independent_oracle_cases":164976, "tops":result,
        "threshold_vs_original_area_change_pct":100*(alt["area_um2"]/orig["area_um2"]-1),
        "threshold_vs_original_ltp_edge_change_pct":100*(alt["longest_topological_path_edges"]/orig["longest_topological_path_edges"]-1),
        "threshold_vs_original_cell_count_change_pct":100*(alt["mapped_cells"]/orig["mapped_cells"]-1)
    },indent=2,sort_keys=True))

if __name__ == "__main__":
    try:
        run()
    except (ValueError, AssertionError, zipfile.BadZipFile) as exc:
        print(f"FAIL_CLOSED: {exc}",file=sys.stderr)
        sys.exit(2)
