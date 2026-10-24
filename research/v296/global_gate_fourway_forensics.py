#!/usr/bin/env python3
"""Independent reproduction of V296 Actions run 40069058725.

Download the four artifacts and rename as v296-{pairwise,serial,parallel,original}-global.zip.
Run: python3 research/v296/global_gate_fourway_forensics.py DIRECTORY
Does not import the production audit parser.
"""
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

FROZEN = {
    "pairwise": ("pairwise", "3a571b343a09631c2a8c561e89fd39b03db8c638ba54b84e6392d8e918d56746", "pareto_global_final", 7911.106436608861, 0.004863, 0, 2, None),
    "serial": ("serial_onehot", "adca74b536f30c37204145795608e957aba5bb47b1bee740cbe2528d1603e87b", "pareto_fourth_repaired", 9996.812266876987, -0.532275, 0, 4, "GRT-0116"),
    "parallel": ("parallel_onehot", "edf2f935b8bec213436568b67e6dca18048d6b664569ac0ce5e3b3b5a5d8f10c", "placed", 8223.921987848826, -4.125862, 3850, 432, "DPL-0036"),
    "original": ("original", "f231b3c0d708b0a8396774f607386e990076b2f1a165edcfa034d97079a2d933", "pareto_control_fifth_repaired", 10208.814238410469, -1.435621, 0, 4, "GRT-0116"),
}

def inspect(root):
    rows = []
    for short, (variant, digest, last, area, slack, slew, cap, error) in FROZEN.items():
        path = Path(root) / f"v296-{short}-global.zip"
        blob = path.read_bytes()
        assert hashlib.sha256(blob).hexdigest() == digest, f"Artifact hash mismatch: {short}"
        with zipfile.ZipFile(path) as archive:
            log = archive.read(f"{variant}.high.log").decode("utf-8")
            names = archive.namelist()
        closed = list(re.finditer(r"(?m)^V296_STAGE_END (\w+)\s*$", log))
        assert closed and closed[-1].group(1) == last, (short, "Last stage mismatch")
        match = re.search(r"(?ms)^V296_STAGE_BEGIN " + last +
                          r"\s*\n(.*?)^V296_STAGE_END " + last + r"\s*$", log)
        assert match, f"Missing closed stage {last}"
        lines = match.group(1).splitlines()
        metric = next((s for s in lines if s.startswith("V296_METRIC stage=" + last + " ")), None)
        assert metric
        vals = dict(re.findall(r"(area_um2|slew|cap)=([-+\d.eE]+)", metric))
        worst = next((s for s in lines if s.startswith("worst slack ")), None)
        assert worst
        observed = (float(vals["area_um2"]), float(worst.split()[-1]),
                    int(vals["slew"]), int(vals["cap"]))
        assert all(abs(a-b) < 1e-6 for a,b in zip(observed, (area, slack, slew, cap)))
        assert error in log if error else "V296_GLOBAL_GATE_ONLY_COMPLETE_NOT_SIGNOFF" in log
        final_def = f"{variant}.high.global.def" in names
        assert final_def == (short == "pairwise")
        rows.append({"variant": variant, "last_stage": last,
                     "area_um2": observed[0], "area_headroom_um2": 7400-observed[0],
                     "ideal_clock_setup_ns": observed[1],
                     "slew_violations": observed[2], "cap_violations": observed[3],
                     "global_route_complete": final_def,
                     "termination": error or "area/cap failure after global route"})
    assert all(r["area_headroom_um2"] < 0 for r in rows)
    assert rows[0]["cap_violations"] == 2
    print(json.dumps({"run": 40069058725, "outcome": "FOUR_WAY_GLOBAL_FEASIBILITY_FAIL",
                      "physical_signoff": False, "rows": rows}, indent=2))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: global_gate_fourway_forensics.py ARTIFACT_DIRECTORY")
    inspect(sys.argv[1])
