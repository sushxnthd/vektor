#!/usr/bin/env python3
"""V309 frozen QV100 DRAM bus-width sensitivity; no physical GPU claim."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from legacy_qv100_runtime import simulate
from qv100_runtime_counter_audit import audit

BASE = 16
VARIANTS = (8, 32)
OPTION = "-gpgpu_dram_buswidth"
ACTIVE = re.compile(r"(?m)^([ \t]*-gpgpu_dram_buswidth[ \t]+)([0-9]+)([ \t]*(?:#.*)?)$")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def perturb(blob, width):
    if width not in VARIANTS:
        raise ValueError("width not preregistered")
    source = blob.decode("utf-8")
    found = list(ACTIVE.finditer(source))
    if len(found) != 1 or int(found[0].group(2)) != BASE:
        raise ValueError("baseline bus-width missing, duplicated or drifted")
    m = found[0]
    result = source[:m.start(2)] + str(width) + source[m.end(2):]
    if result[:m.start(2)] != source[:m.start(2)] or result[m.start(2)+len(str(width)):] != source[m.end(2):]:
        raise ValueError("unapproved mutation")
    return result.encode("utf-8")


def prepare(config, folder):
    original = Path(config).read_bytes()
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    for width in VARIANTS:
        data = perturb(original, width)
        filename = "buswidth-%d.config" % width
        target = folder / filename
        if target.exists():
            raise ValueError("refusing to overwrite frozen variant")
        target.write_bytes(data)
        rows.append({"buswidth_bytes": width, "filename": filename, "sha256": digest(data)})
    manifest = {
        "source_sha256": digest(original),
        "baseline_buswidth_bytes": BASE,
        "variants": rows,
        "only_changed_option": OPTION,
        "predictions": {
            "p1_narrower_is_slower": "cycles(8) > cycles(16)",
            "p2_wider_not_slower": "cycles(32) <= cycles(16)",
            "p3_small_widening_benefit": "(cycles(16)-cycles(32))/cycles(16) < 0.02"
        },
        "evidence_tier": "simulator_parameter_sensitivity_only",
        "physical_speedup_claim_allowed": False
    }
    (folder / "buswidth-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n")
    return manifest


def verify(folder, source=None):
    folder = Path(folder)
    manifest = json.loads((folder / "buswidth-manifest.json").read_text())
    if manifest["baseline_buswidth_bytes"] != BASE or [r["buswidth_bytes"] for r in manifest["variants"]] != list(VARIANTS):
        raise ValueError("experiment identity drift")
    if manifest["only_changed_option"] != OPTION:
        raise ValueError("changed option drift")
    if source is not None and digest(source) != manifest["source_sha256"]:
        raise ValueError("source config digest drift")
    for row in manifest["variants"]:
        if row["filename"] != "buswidth-%d.config" % row["buswidth_bytes"]:
            raise ValueError("filename drift")
        data = (folder / row["filename"]).read_bytes()
        if digest(data) != row["sha256"]:
            raise ValueError("variant digest drift")
        if source is not None and data != perturb(source, row["buswidth_bytes"]):
            raise ValueError("unapproved config change")
    return manifest


def execute(binary, trace, gpgpu, trace_config, selection, folder, evidence):
    manifest = verify(folder, Path(gpgpu).read_bytes())
    rows = []
    for row in manifest["variants"]:
        width = row["buswidth_bytes"]
        result = simulate(binary, trace, Path(folder) / row["filename"], trace_config,
                          Path(evidence) / ("buswidth-%d" % width), selection)
        rows.append({"buswidth_bytes": width, "status": result["status"]})
    if any(r["status"] != "PASS_RUNTIME" for r in rows):
        raise ValueError("variant simulation failed closed")
    return rows


def summarize(base, variants):
    cycles = base["total_sim_cycles"]
    instructions = base["total_sim_instructions"]
    launches = base["expected_launches"]
    if min(cycles, instructions, launches) <= 0 or sorted(variants) != list(VARIANTS):
        raise ValueError("invalid experiment identity or baseline")
    keys = ("L1D_total_cache_misses", "L2_total_cache_misses")
    rows = []
    for width in VARIANTS:
        result = variants[width]
        if result["expected_launches"] != launches or result["total_sim_instructions"] != instructions:
            raise ValueError("unmatched workload launches/instructions")
        c = result["total_sim_cycles"]
        if c <= 0:
            raise ValueError("nonpositive simulated cycles")
        counters = {k: result["cumulative_counter_totals"].get(k) for k in keys}
        rows.append({
            "buswidth_bytes": width, "sim_cycles": c,
            "cycle_delta": c-cycles,
            "cycle_delta_percent": 100.0*(c/cycles-1),
            "counters": counters,
            "cache_counters_match_baseline": all(
                counters[k] == base["cumulative_counter_totals"].get(k) for k in keys)
        })
    narrow, wide = rows
    return {
        "status": "PASS_INDEPENDENT_BUSWIDTH_AUDIT",
        "baseline_sim_cycles": cycles,
        "baseline_sim_instructions": instructions,
        "baseline_cache_counters": {k:base["cumulative_counter_totals"].get(k) for k in keys},
        "variants": rows,
        "predictions": {
            "p1_narrower_is_slower": narrow["sim_cycles"] > cycles,
            "p2_wider_not_slower": wide["sim_cycles"] <= cycles,
            "p3_small_widening_benefit": (cycles-wide["sim_cycles"])/cycles < 0.02
        },
        "counter_invariance": all(r["cache_counters_match_baseline"] for r in rows),
        "hardware_calibrated": False,
        "equal_resource_architecture_comparison": False,
        "physical_speedup_demonstrated": False
    }


def inspect(folder, evidence, selection):
    manifest = verify(folder)
    evidence = Path(evidence)
    def read(path):
        return audit((path/"repeat-1.log").read_bytes(), (path/"repeat-2.log").read_bytes(),
                     selection["kernel_launches"])
    base = read(evidence)
    variants = {r["buswidth_bytes"]:read(evidence/("buswidth-%d" % r["buswidth_bytes"]))
                for r in manifest["variants"]}
    result = summarize(base, variants)
    result["raw_log_sha256"] = {"baseline":base["raw_log_sha256"],
                                **{str(k):v["raw_log_sha256"] for k,v in variants.items()}}
    result["manifest_sha256"] = digest((Path(folder)/"buswidth-manifest.json").read_bytes())
    return result


def selftest():
    source = b"# -gpgpu_dram_buswidth 99\n-gpgpu_dram_buswidth 16 # HBM\n-dram_latency 100\n"
    for width in VARIANTS:
        expected = source.replace(b"-gpgpu_dram_buswidth 16", ("-gpgpu_dram_buswidth %d"%width).encode())
        assert perturb(source, width) == expected
    bads = [source+b"-gpgpu_dram_buswidth 16\n",
            source.replace(b"buswidth 16",b"buswidth 12"),
            b"# -gpgpu_dram_buswidth 16\n",
            source.replace(b"buswidth 16",b"buswidth 16x")]
    for bad in bads:
        try:
            perturb(bad, 8)
        except ValueError:
            pass
        else:
            raise AssertionError("malformed source accepted")
    def row(c, ins=100, n=4, l1=20, l2=5):
        return {"total_sim_cycles":c,"total_sim_instructions":ins,"expected_launches":n,
                "cumulative_counter_totals":{"L1D_total_cache_misses":l1,"L2_total_cache_misses":l2},
                "raw_log_sha256":["a","b"]}
    good = summarize(row(100), {8:row(120),32:row(99)})
    assert all(good["predictions"].values()) and good["counter_invariance"]
    assert not summarize(row(100), {8:row(99),32:row(101)})["predictions"]["p1_narrower_is_slower"]
    assert not summarize(row(100), {8:row(110),32:row(90)})["predictions"]["p3_small_widening_benefit"]
    assert not summarize(row(100), {8:row(110,l1=21),32:row(99)})["counter_invariance"]
    for wrong in [{8:row(110,ins=99),32:row(99)}, {8:row(110),32:row(99,n=5)}, {8:row(110)}]:
        try:
            summarize(row(100), wrong)
        except ValueError:
            pass
        else:
            raise AssertionError("unmatched or missing variant accepted")
    return {"status":"PASS","positive_controls":5,"negative_controls":9}


def main():
    parser = argparse.ArgumentParser()
    for name in ("selftest","run","audit"):
        parser.add_argument("--"+name, action="store_true")
    for name in ("prepare","folder","binary","trace","gpgpu","trace-config","selection","evidence","out"):
        parser.add_argument("--"+name)
    args = parser.parse_args()
    if args.selftest:
        result = selftest()
    elif args.prepare:
        result = prepare(args.prepare,args.folder)
    elif args.run:
        result = execute(args.binary,args.trace,args.gpgpu,args.trace_config,
                         json.loads(Path(args.selection).read_text()),args.folder,args.evidence)
    elif args.audit:
        result = inspect(args.folder,args.evidence,json.loads(Path(args.selection).read_text()))
        Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    else:
        parser.error("choose --selftest, --prepare, --run, or --audit")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
