#!/usr/bin/env python3
"""Independent fail-closed V296 post-CTS, propagated-clock extracted audit."""
import json
import math
import re
import sys
from pathlib import Path

VARIANTS = ("pairwise", "serial_onehot")
NUM = r"([-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?)"
AREA_LIMIT = 7400.0
SETUP_GUARD_NS = 0.050


def one_value(log, prefix):
    matches = re.findall(r"(?m)^" + re.escape(prefix) + r"([^\r\n]+)\r?$", log)
    if len(matches) != 1:
        raise ValueError("Missing/duplicate marker " + prefix)
    return matches[0].strip()


def numeric(log, prefix):
    value = float(one_value(log, prefix))
    if not math.isfinite(value):
        raise ValueError("Nonfinite " + prefix)
    return value


def stage(log, name):
    m = re.search(r"(?ms)^V296_STAGE_BEGIN " + re.escape(name) +
                  r"\r?\n(.*?)^V296_STAGE_END " + re.escape(name) + r"\r?$", log)
    if not m:
        raise ValueError("Missing complete stage " + name)
    body = m.group(1)
    metrics = re.findall(r"(?m)^V296_METRIC stage=" + re.escape(name) +
                         r" area_um2=" + NUM + r" slew=(\d+) cap=(\d+)\r?$", body)
    slack = re.findall(r"(?mi)^worst slack(?:\s+max)?\s+" + NUM + r"\s*$", body)
    if len(metrics) != 1 or len(slack) != 1:
        raise ValueError("Missing/ambiguous metrics " + name)
    area = float(metrics[0][0])
    setup = float(slack[0])
    if not math.isfinite(area) or area <= 0 or not math.isfinite(setup):
        raise ValueError("Invalid metrics " + name)
    return {"area_um2": area, "setup_ns": setup,
            "slew": int(metrics[0][1]), "cap": int(metrics[0][2])}


def case(root, variant):
    if variant not in VARIANTS:
        raise ValueError("Unknown contestant")
    logpath = root / (variant + ".high.log")
    if not logpath.is_file():
        return {"variant": variant, "complete": False, "error": "missing log"}
    log = logpath.read_text(errors="replace")
    result = {"variant": variant, "complete": False,
              "evidence_tier": "post-CTS propagated-clock detailed-route OpenRCX; not signoff"}
    if "V296_CTS45_DONE" not in log.splitlines():
        result["last_marker"] = next((x for x in reversed(log.splitlines())
                                       if x.startswith("V296_CTS45_")), "none")
        return result
    expected = {"V296_CLOCK_PERIOD_NS ": "3.5",
                "V296_PLACE_DENSITY ": "0.45",
                "V296_CTS45_VARIANT ": variant,
                "V296_CTS45_EXTRA_REPAIR ": str(int(variant == "serial_onehot")),
                "V296_CTS45_CLOCKS_PROPAGATED ": "1",
                "V296_CTS45_RC_MULTIPLIER ": "2.0",
                "V296_CTS45_DRC_COUNT ": "0",
                "V296_CTS45_IS_ROUTED ": "1"}
    for prefix, value in expected.items():
        if one_value(log, prefix) != value:
            raise ValueError("Wrong frozen setting " + prefix)
    required = ("V296_CTS45_FOURTH_DONE", "V296_CTS45_CTS_BEGIN",
                "V296_CTS45_CTS_END", "V296_CTS45_DETAIL_BEGIN",
                "V296_CTS45_HOLD_BEGIN", "V296_CTS45_HOLD_END",
                "V296_CTS45_DONE")
    lines = log.splitlines()
    for marker in required:
        if lines.count(marker) != 1:
            raise ValueError("Missing/duplicate CTS marker " + marker)
    if not (log.index("V296_CTS45_CTS_BEGIN") <
            log.index("V296_CTS45_CLOCKS_PROPAGATED") <
            log.index("V296_CTS45_CTS_END") <
            log.index("V296_CTS45_DETAIL_BEGIN") <
            log.index("V296_CTS45_RC_MULTIPLIER") <
            log.index("V296_CTS45_DONE")):
        raise ValueError("CTS not before routing/extraction")
    fifth = "V296_CTS45_FIFTH_DONE" in lines
    if fifth != (variant == "serial_onehot"):
        raise ValueError("Wrong control fifth repair")
    pre = numeric(log, "V296_CTS45_PRECTS_AREA_UM2 ")
    post = numeric(log, "V296_CTS45_POSTCTS_AREA_UM2 ")
    if pre <= 0 or post <= pre:
        raise ValueError("Clock-tree area not positively accounted")
    for stage_name in ("cts45_clock_tree", "cts45_postcts_repaired",
                       "cts45_postcts_global", "cts45_extracted"):
        stage(log, stage_name)
    final = stage(log, "cts45_extracted")
    hold_block = re.search(r"(?ms)^V296_CTS45_HOLD_BEGIN\r?\n(.*?)^V296_CTS45_HOLD_END", log)
    holds = re.findall(r"(?mi)^worst slack(?:\s+min)?\s+" + NUM + r"\s*$",
                       hold_block.group(1)) if hold_block else []
    if len(holds) != 1:
        raise ValueError("Missing/ambiguous propagated hold")
    final["hold_ns"] = float(holds[0])
    if not math.isfinite(final["hold_ns"]):
        raise ValueError("Nonfinite hold")
    stem = root / (variant + ".high")
    def_files = [Path(str(stem) + "." + suffix + ".def")
                 for suffix in ("prects", "postcts", "cts45")]
    spef = Path(str(stem) + ".cts45.spef")
    drc = Path(str(stem) + ".cts45.drc.rpt")
    if any(not f.is_file() or f.stat().st_size == 0 for f in def_files + [spef]) or not drc.is_file():
        raise ValueError("Missing CTS DEF, extracted SPEF or DRC")
    before = def_files[0].read_text(errors="replace")
    after = def_files[1].read_text(errors="replace")
    # Independent structural evidence of inserted CTS buffers.
    def clkbuf_count(deftext):
        return len(re.findall(r"(?m)^\s*-\s+\S+\s+CLKBUF_X[123]\b", deftext))
    clock_buffer_delta = clkbuf_count(after) - clkbuf_count(before)
    if clock_buffer_delta <= 0:
        raise ValueError("No new CTS clock buffers in post-CTS DEF")
    spef_text = spef.read_text(errors="replace")
    if "*SPEF" not in spef_text or "*D_NET" not in spef_text:
        raise ValueError("Malformed SPEF")
    result.update(complete=True, prects_area_um2=pre, postcts_area_um2=post,
                  clock_tree_increment_um2=post - pre,
                  new_clkbuf_instances=clock_buffer_delta, final=final,
                  feasible=(final["area_um2"] <= AREA_LIMIT and
                            final["setup_ns"] >= SETUP_GUARD_NS and
                            final["hold_ns"] >= 0 and
                            final["slew"] == 0 and final["cap"] == 0))
    return result


def aggregate(root):
    rows = {}
    for variant in VARIANTS:
        try:
            rows[variant] = case(root, variant)
        except (ValueError, OSError) as exc:
            rows[variant] = {"variant": variant, "complete": False, "error": str(exc)}
    p, c = (rows[name] for name in VARIANTS)
    decision = "INCOMPLETE_NO_CTS_CLAIM"
    comparison = None
    if p.get("complete") and c.get("complete"):
        pv, cv = p["final"], c["final"]
        saving = (cv["area_um2"] - pv["area_um2"]) / cv["area_um2"]
        lead = pv["setup_ns"] - cv["setup_ns"]
        comparison = {"area_saving_fraction": saving, "setup_lead_ns": lead,
                      "candidate_feasible": p["feasible"], "control_feasible": c["feasible"],
                      "strict_equal_consumed_area": False}
        if not p["feasible"]:
            decision = "CANDIDATE_CTS_PHYSICAL_GATE_FAIL"
        elif not c["feasible"]:
            decision = "CONTROL_CTS_INFEASIBLE_NO_PARETO_CLAIM"
        elif saving + 1e-12 >= 0.10 and lead + 1e-12 >= 0.200:
            decision = "PREDICTED_CTS_PARETO_SURVIVES"
        else:
            decision = "PREDICTED_CTS_PARETO_FALSIFIED"
    elif p.get("complete") and not p["feasible"]:
        decision = "CANDIDATE_CTS_PHYSICAL_GATE_FAIL"
    return {"decision": decision, "rows": rows, "comparison": comparison,
            "workload_holdouts": "SEALED", "power": "NOT_EVALUATED",
            "equal_consumed_area": "NOT_EVALUATED", "signoff": False}


def self_test():
    import tempfile
    def mk(root, variant, setup, area):
        extra = int(variant == "serial_onehot")
        def block(name, area, setup):
            return (f"V296_STAGE_BEGIN {name}\nV296_METRIC stage={name} "
                    f"area_um2={area} slew=0 cap=0\nworst slack {setup}\n"
                    f"V296_STAGE_END {name}\n")
        log = ("V296_CLOCK_PERIOD_NS 3.5\nV296_PLACE_DENSITY 0.45\n"
               f"V296_CTS45_VARIANT {variant}\nV296_CTS45_EXTRA_REPAIR {extra}\n"
               "V296_CTS45_FOURTH_DONE\n" +
               ("V296_CTS45_FIFTH_DONE\n" if extra else "") +
               "V296_CTS45_PRECTS_AREA_UM2 5000\nV296_CTS45_CTS_BEGIN\n"
               "V296_CTS45_CLOCKS_PROPAGATED 1\nV296_CTS45_POSTCTS_AREA_UM2 5100\n" +
               block("cts45_clock_tree", 5100, setup) +
               "V296_CTS45_CTS_END\n" +
               block("cts45_postcts_repaired", 5300, setup) +
               block("cts45_postcts_global", 5400, setup) +
               "V296_CTS45_DETAIL_BEGIN\nV296_CTS45_DRC_COUNT 0\n"
               "V296_CTS45_IS_ROUTED 1\nV296_CTS45_RC_MULTIPLIER 2.0\n"
               "V296_CTS45_HOLD_BEGIN\nworst slack 0.2\nV296_CTS45_HOLD_END\n" +
               block("cts45_extracted", area, setup) + "V296_CTS45_DONE\n")
        (root / (variant + ".high.log")).write_text(log)
        stem = root / (variant + ".high")
        for suffix, text in (("prects.def", "VERSION 5.8 ;\n"),
                             ("postcts.def", "VERSION 5.8 ;\n - clkbuf_0 CLKBUF_X3 + PLACED ;\n"),
                             ("cts45.def", "VERSION 5.8 ;\n"),
                             ("cts45.spef", '*SPEF "IEEE 1481-1998"\n*D_NET clk 1\n'),
                             ("cts45.drc.rpt", "")):
            Path(str(stem) + "." + suffix).write_text(text)
        return log
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        p_log = mk(root, "pairwise", 0.31, 6000)
        mk(root, "serial_onehot", 0.1, 7000)
        assert aggregate(root)["decision"] == "PREDICTED_CTS_PARETO_SURVIVES"
        p = root / "pairwise.high.log"
        for replacement in ("V296_CLOCK_PERIOD_NS 4.0", "V296_CTS45_CLOCKS_PROPAGATED 0",
                            "V296_CTS45_RC_MULTIPLIER 1.0"):
            key = replacement.split()[0]
            changed = re.sub(r"(?m)^" + key + r" .*$", replacement, p_log)
            p.write_text(changed)
            assert not aggregate(root)["rows"]["pairwise"].get("complete")
        p.write_text(p_log.replace("V296_CTS45_DONE", "V296_CTS45_ABORT"))
        assert aggregate(root)["decision"] == "INCOMPLETE_NO_CTS_CLAIM"
        p.write_text(p_log)
        (root / "pairwise.high.postcts.def").write_text("VERSION 5.8 ;\n")
        assert not aggregate(root)["rows"]["pairwise"].get("complete")
    print("V296_CTS45_INDEPENDENT_AUDIT_SELFTEST_PASS")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
    elif len(sys.argv) == 4 and sys.argv[1] == "--single":
        root, variant = Path(sys.argv[2]), sys.argv[3]
        outcome = case(root, variant)
        (root / (variant + ".audit.json")).write_text(json.dumps(outcome, indent=2) + "\n")
        print(json.dumps(outcome, indent=2))
        if not outcome.get("complete"):
            raise SystemExit(3)
    elif len(sys.argv) == 3 and sys.argv[1] == "--aggregate":
        root = Path(sys.argv[2])
        outcome = aggregate(root)
        (root / "aggregate.json").write_text(json.dumps(outcome, indent=2) + "\n")
        print(json.dumps(outcome, indent=2))
        if outcome["decision"] != "PREDICTED_CTS_PARETO_SURVIVES":
            raise SystemExit(3)
    else:
        raise SystemExit("Usage: --self-test | --single ROOT VARIANT | --aggregate ROOT")
