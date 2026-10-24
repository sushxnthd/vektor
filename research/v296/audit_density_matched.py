#!/usr/bin/env python3
"""Independent fail-closed V296 matched-density audit; global route is not signoff."""
import json
import math
import re
import sys
from pathlib import Path

VARIANTS = ("pairwise", "serial_onehot", "original")
DENSITIES = {"d045": "0.45", "d065": "0.65"}
STAGES = ("placed", "repaired_first", "routed_first", "repaired_second",
          "routed_final", "repaired_third", "routed_third",
          "pareto_fourth_repaired", "pareto_fourth_routed",
          "pareto_control_fifth_repaired", "pareto_control_fifth_routed",
          "pareto_global_final")
NUM = r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)"
AREA_CEILING = 7400.0
SETUP_GUARDBAND_NS = 0.050


def stage_metrics(log, stage):
    m = re.search(r"(?ms)^V296_STAGE_BEGIN " + re.escape(stage) +
                  r"\r?\n(.*?)^V296_STAGE_END " + re.escape(stage) + r"\r?$", log)
    if not m:
        return None
    block = m.group(1)
    a = re.search(r"(?m)^V296_METRIC stage=" + re.escape(stage) +
                  r" area_um2=" + NUM + r" slew=(\d+) cap=(\d+)\r?$", block)
    t = re.search(r"(?mi)^worst slack(?:\s+max)?\s+" + NUM + r"\s*$", block)
    if not a or not t:
        raise ValueError("malformed stage " + stage)
    v = {"area_um2": float(a.group(1)), "slew": int(a.group(2)),
         "cap": int(a.group(3)), "setup_ns": float(t.group(1))}
    if not all(math.isfinite(x) for x in v.values()) or v["area_um2"] <= 0:
        raise ValueError("invalid stage " + stage)
    return v


def evaluate(log, variant, density, has_def):
    if variant not in VARIANTS or density not in DENSITIES:
        raise ValueError("invalid identity")
    lines = set(log.splitlines())
    extra = 0 if variant == "pairwise" else 1
    required = ("V296_CLOCK_PERIOD_NS 3.5",
                "V296_PLACE_DENSITY " + DENSITIES[density])
    for marker in required:
        if marker not in lines:
            raise ValueError("missing frozen marker " + marker)
    for prefix, expected in (("V296_CLOCK_PERIOD_NS ", required[0]),
                             ("V296_PLACE_DENSITY ", required[1]),
                             ("V296_PARETO_VARIANT ", "V296_PARETO_VARIANT " + variant),
                             ("V296_PARETO_EXTRA_REPAIR ", "V296_PARETO_EXTRA_REPAIR " + str(extra))):
        if any(x.startswith(prefix) and x != expected for x in lines):
            raise ValueError("contradictory marker " + prefix)
    stages = {x: v for x in STAGES if (v := stage_metrics(log, x)) is not None}
    markers = ("V296_PARETO_VARIANT " + variant,
               "V296_PARETO_EXTRA_REPAIR " + str(extra),
               "V296_PARETO_FOURTH_DONE",
               "V296_GLOBAL_GATE_ONLY 1",
               "V296_GLOBAL_GATE_ONLY_COMPLETE_NOT_SIGNOFF")
    complete = (has_def and all(x in lines for x in markers) and
                "pareto_global_final" in stages and
                "V296_PARETO_DETAIL_BEGIN" not in lines and
                (("V296_PARETO_CONTROL_FIFTH_DONE" in lines and
                  "pareto_control_fifth_routed" in stages) if extra else
                 "V296_PARETO_CONTROL_FIFTH_DONE" not in lines))
    final = stages.get("pareto_global_final") if complete else None
    feasible = None if final is None else (
        final["area_um2"] <= AREA_CEILING and final["slew"] == 0 and
        final["cap"] == 0 and final["setup_ns"] >= SETUP_GUARDBAND_NS)
    last = next((x for x in reversed(STAGES) if x in stages), None)
    return {"variant": variant, "density": DENSITIES[density],
            "complete_global_route": bool(complete),
            "last_stage": last, "last_metrics": stages.get(last),
            "final": final, "feasible_with_50ps_ideal_guardband": feasible,
            "evidence_tier": "ideal-clock global-route only; NOT signoff"}


def report(root):
    rows = {}
    for tag in DENSITIES:
        for variant in VARIANTS:
            stem = variant + "." + tag
            log = root / (stem + ".high.log")
            df = root / (stem + ".high.global.def")
            if not log.is_file():
                rows[stem] = {"error": "missing log", "feasible_with_50ps_ideal_guardband": None}
                continue
            try:
                rows[stem] = evaluate(log.read_text(), variant, tag,
                                      df.is_file() and df.stat().st_size > 0)
            except (ValueError, OSError) as exc:
                rows[stem] = {"error": str(exc), "feasible_with_50ps_ideal_guardband": None}
    pred = {"pairwise.d045": True, "pairwise.d065": False}
    checks = {k: ("INCONCLUSIVE" if rows[k]["feasible_with_50ps_ideal_guardband"] is None
                  else "SUPPORTED" if rows[k]["feasible_with_50ps_ideal_guardband"] == v
                  else "FALSIFIED") for k, v in pred.items()}
    comparisons = {}
    for tag in DENSITIES:
        p = rows["pairwise." + tag]
        comparisons[tag] = {}
        for control in VARIANTS[1:]:
            c = rows[control + "." + tag]
            if p.get("feasible_with_50ps_ideal_guardband") is True and c.get("feasible_with_50ps_ideal_guardband") is True:
                comparisons[tag][control] = {
                    "global_only_pareto": (p["final"]["area_um2"] < c["final"]["area_um2"] and
                                           p["final"]["setup_ns"] > c["final"]["setup_ns"]),
                    "area_delta_um2": c["final"]["area_um2"] - p["final"]["area_um2"],
                    "slack_delta_ns": p["final"]["setup_ns"] - c["final"]["setup_ns"]}
            else:
                comparisons[tag][control] = "NO_MATCHED_FEASIBLE_COMPARISON"
    status = ("INCOMPLETE" if any(x.get("feasible_with_50ps_ideal_guardband") is None for x in rows.values())
              else "PREDICTIONS_FALSIFIED" if "FALSIFIED" in checks.values()
              else "PREDICTIONS_SUPPORTED_GLOBAL_ONLY")
    return {"status": status, "predictions": checks, "comparisons": comparisons,
            "rows": rows, "physical_signoff": "NOT_EVALUATED",
            "strict_equal_consumed_area": "NOT_EVALUATED",
            "workload_holdouts": "SEALED"}


def self_test():
    def block(stage, area, slack, cap=0):
        return (f"V296_STAGE_BEGIN {stage}\nV296_METRIC stage={stage} "
                f"area_um2={area} slew=0 cap={cap}\nworst slack {slack}\n"
                f"V296_STAGE_END {stage}\n")
    for density in DENSITIES:
        for variant in VARIANTS:
            extra = int(variant != "pairwise")
            log = (f"V296_CLOCK_PERIOD_NS 3.5\nV296_PLACE_DENSITY {DENSITIES[density]}\n"
                   f"V296_PARETO_VARIANT {variant}\nV296_PARETO_EXTRA_REPAIR {extra}\n"
                   "V296_PARETO_FOURTH_DONE\n" +
                   block("pareto_fourth_routed", 6500, 0.1) +
                   ("V296_PARETO_CONTROL_FIFTH_DONE\n" +
                    block("pareto_control_fifth_routed", 6500, 0.1) if extra else "") +
                   "V296_GLOBAL_GATE_ONLY 1\n" +
                   block("pareto_global_final", 6500, 0.1) +
                   "V296_GLOBAL_GATE_ONLY_COMPLETE_NOT_SIGNOFF\n")
            assert evaluate(log, variant, density, True)["feasible_with_50ps_ideal_guardband"] is True
            assert evaluate(log, variant, density, False)["feasible_with_50ps_ideal_guardband"] is None
            assert evaluate(log.replace("area_um2=6500", "area_um2=7500"), variant, density, True)["feasible_with_50ps_ideal_guardband"] is False
            assert evaluate(log.replace("worst slack 0.1", "worst slack 0.01"), variant, density, True)["feasible_with_50ps_ideal_guardband"] is False
            assert evaluate(log.replace("cap=0", "cap=2"), variant, density, True)["feasible_with_50ps_ideal_guardband"] is False
            for broken in (log.replace("3.5", "4.0"), log.replace("0.45", "0.55").replace("0.65", "0.55")):
                try:
                    evaluate(broken, variant, density, True)
                except ValueError:
                    pass
                else:
                    raise AssertionError("accepted corrupted physical identity")
    print("V296_DENSITY_AUDIT_SELFTEST_PASS")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
    elif len(sys.argv) == 3 and sys.argv[1] == "--aggregate":
        root = Path(sys.argv[2])
        result = report(root)
        root.mkdir(parents=True, exist_ok=True)
        (root / "density_audit.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, indent=2, sort_keys=True))
        if result["status"] != "PREDICTIONS_SUPPORTED_GLOBAL_ONLY":
            raise SystemExit(3)
    elif len(sys.argv) == 5 and sys.argv[1] == "--single":
        root, variant, density = Path(sys.argv[2]), sys.argv[3], sys.argv[4]
        stem = variant + "." + density
        log = root / (stem + ".high.log")
        df = root / (stem + ".high.global.def")
        row = evaluate(log.read_text(), variant, density,
                       df.is_file() and df.stat().st_size > 0)
        (root / (stem + ".audit.json")).write_text(json.dumps(row, indent=2, sort_keys=True) + "\n")
        print(json.dumps(row, indent=2, sort_keys=True))
        if not row["complete_global_route"]:
            raise SystemExit(3)
    else:
        raise SystemExit("Usage: --self-test | --single ROOT VARIANT d045/d065 | --aggregate ROOT")
