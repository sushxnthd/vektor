#!/usr/bin/env python3
"""Read-only SPEF coupling/activity boundary for SHA-locked V296 routed artifacts.

External capacitive-energy proxy only; NOT measured power, signoff, or GPU speedup.
"""
import argparse
import hashlib
import json
import math
import re
import zipfile
from pathlib import Path

HASHES = {
    "pairwise": "9ce2ede807ba5858efcd113b3cd4c2f9e8e5d4a6d97a7b04eb663dd354786259",
    "serial_onehot": "5c0f7ef91a2151ac2069553cd93a34b97d38c939d6f1106ea95ef4cc8b85706e",
}
SOURCE_RUN = 40173311725
FLOAT = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"


def number(raw):
    x = float(raw)
    if not math.isfinite(x) or x < 0:
        raise ValueError("Nonfinite or negative capacitance")
    return x


def parse_spef(text):
    if len(re.findall(r"(?m)^\*C_UNIT\s+1\s+PF\s*$", text)) != 1:
        raise ValueError("SPEF must declare exactly one *C_UNIT 1 PF")
    header = text.split("*D_NET", 1)[0]
    names = dict(re.findall(r"(?m)^\*(\d+)\s+(\S+)\s*$", header))

    def resolve(n):
        m = re.match(r"^\*(\d+)(.*)$", n)
        return names.get(m.group(1), "*" + m.group(1)) + m.group(2) if m else n

    net_re = re.compile(r"(?ms)^\*D_NET\s+(\S+)\s+(" + FLOAT + r")\s*\n(.*?)^\*END\s*$")
    blocks = list(net_re.finditer(text))
    if not blocks or len(re.findall(r"(?m)^\*D_NET\b", text)) != len(blocks):
        raise ValueError("Missing or unparsed D_NET block")
    ground = 0.0
    coupling_entries = 0
    couplings = {}
    totals = []
    max_local = ("", 0.0)
    for match in blocks:
        net, declared, body = match.groups()
        totals.append(number(declared))
        sections = re.findall(r"(?ms)^\*CAP\s*\n(.*?)(?=^\*(?:RES|END|INDUC)\b)", body)
        if len(sections) != 1:
            raise ValueError("Missing or ambiguous CAP section for " + net)
        local = 0.0
        for line in sections[0].splitlines():
            if not line.strip() or line.lstrip().startswith("//"):
                continue
            f = line.split()
            if len(f) not in (3, 4) or not f[0].isdigit():
                raise ValueError("Unexpected CAP record: " + line[:120])
            cap = number(f[-1])
            if len(f) == 3:
                ground += cap
            else:
                coupling_entries += 1
                a, b = sorted((resolve(f[1]), resolve(f[2])))
                if a == b:
                    raise ValueError("Degenerate two-terminal CAP")
                key = (a, b)
                if key in couplings:
                    if not math.isclose(couplings[key], cap, rel_tol=1e-7, abs_tol=1e-10):
                        raise ValueError("Conflicting duplicate coupling entry")
                else:
                    couplings[key] = cap
                local += cap
        if local > max_local[1]:
            max_local = (resolve(net), local)
    cc = sum(couplings.values())
    dnet = sum(totals)
    return {
        "net_count": len(blocks), "sum_declared_dnet_pf": dnet,
        "ground_cap_pf": ground, "unique_coupling_cap_pf": cc,
        "coupling_entries": coupling_entries,
        "unique_coupling_pairs": len(couplings),
        "duplicate_coupling_entries": coupling_entries - len(couplings),
        "dnet_minus_ground_plus_one_coupling_pf": dnet - (ground + cc),
        "dnet_minus_ground_plus_two_couplings_pf": dnet - (ground + 2 * cc),
        "largest_block_coupling_pf": max_local[1],
        "largest_block_coupling_net": max_local[0],
    }


def effective_cap(row, rho):
    if not -1 <= rho <= 1:
        raise ValueError("Correlation outside [-1,1]")
    return row["ground_cap_pf"] + 2 * row["unique_coupling_cap_pf"] * (1 - rho)


def boundary(p, s):
    corners = {}
    for rho in (-1, 0, 1):
        pp, ss = effective_cap(p, rho), effective_cap(s, rho)
        corners[str(rho)] = {
            "rho": rho, "pairwise_effective_cap_pf": pp,
            "serial_effective_cap_pf": ss,
            "pairwise_over_serial": pp / ss if ss else None,
            "pairwise_activity_break_even": ss / pp if pp else None,
            "candidate_lower_at_equal_activity": pp < ss,
        }
    return {
        "model": "E_ext proportional to alpha*V^2/2 * [Cg + 2*Cc*(1-rho)]",
        "equal_rho_corners": corners,
        "robust_equal_rho_advantage": all(x["candidate_lower_at_equal_activity"] for x in corners.values()),
        "worst_candidate_vs_best_control_ratio":
            effective_cap(p, -1) / effective_cap(s, 1) if effective_cap(s, 1) else None,
        "guaranteed_against_independent_correlations": effective_cap(p, -1) < effective_cap(s, 1),
        "ground_cap_ratio": p["ground_cap_pf"] / s["ground_cap_pf"] if s["ground_cap_pf"] else None,
        "unique_coupling_cap_ratio": p["unique_coupling_cap_pf"] / s["unique_coupling_cap_pf"] if s["unique_coupling_cap_pf"] else None,
    }


def read_zip(path, variant):
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if digest != HASHES[variant]:
        raise ValueError("Original artifact SHA-256 mismatch for " + variant)
    with zipfile.ZipFile(path) as z:
        spef = z.read(variant + ".high.cts45.spef").decode("utf-8")
        log = z.read(variant + ".high.log").decode("utf-8")
        manifest = json.loads(z.read("in_situ_manifest.json"))
    if "V296_CTS45_IS_ROUTED 1" not in log or "V296_CTS45_DRC_COUNT 0" not in log:
        raise ValueError("Source not routed or DRC clean")
    row = parse_spef(spef)
    row["spef_sha256"] = hashlib.sha256(spef.encode()).hexdigest()
    row["artifact_sha256"] = digest
    row["physical_tcl_sha256"] = manifest["original_tcl_sha256"]
    return row


def analyze(pairwise, serial):
    p, s = read_zip(pairwise, "pairwise"), read_zip(serial, "serial_onehot")
    if p["physical_tcl_sha256"] != s["physical_tcl_sha256"]:
        raise ValueError("Different physical protocols")
    return {
        "decision": "COUPLING_ACTIVITY_PROXY_COMPUTED_NOT_PHYSICAL_CLOSURE",
        "source_run": SOURCE_RUN, "source_evidence": "original SHA-256 verified post-route SPEFs",
        "pairwise": p, "serial_onehot": s, "boundary": boundary(p, s),
        "holdouts": "SEALED", "physical_gate": "BOTH_INFEASIBLE",
        "limitations": "Not measured power. SPEF coupling representation can be approximate; net-level transition correlation, cell internal/clock/glitch/short-circuit energy and timing closure unmeasured. Uniform activity/correlation model only.",
    }


def self_test():
    sample = """*SPEF "IEEE 1481-1998"
*C_UNIT 1 PF
*NAME_MAP
*1 a
*2 b
*D_NET *1 0.7
*CONN
*CAP
1 *1:1 0.3
2 *1:1 *2:1 0.4
*RES
1 *1:1 *1:2 1.0
*END
*D_NET *2 0.6
*CONN
*CAP
1 *2:1 0.2
2 *2:1 *1:1 0.4
*RES
1 *2:1 *2:2 1.0
*END
"""
    a = parse_spef(sample)
    assert a["net_count"] == 2 and a["coupling_entries"] == 2
    assert a["unique_coupling_pairs"] == 1 and a["duplicate_coupling_entries"] == 1
    assert math.isclose(a["ground_cap_pf"], .5) and math.isclose(a["unique_coupling_cap_pf"], .4)
    assert math.isclose(effective_cap(a, 1), .5)
    assert math.isclose(effective_cap(a, 0), 1.3)
    assert math.isclose(effective_cap(a, -1), 2.1)
    b = {**a, "ground_cap_pf": .6, "unique_coupling_cap_pf": .5}
    assert boundary(a, b)["robust_equal_rho_advantage"]
    assert not boundary(b, a)["robust_equal_rho_advantage"]
    assert not boundary(a, b)["guaranteed_against_independent_correlations"]
    for bad in (
        sample.replace("*C_UNIT 1 PF", "*C_UNIT 1 FF"),
        sample.replace("*CAP", "*BAD"),
        sample.replace("0.4\n*RES", "-0.4\n*RES", 1),
        sample.replace("2 *2:1 *1:1 0.4", "2 *2:1 *1:1 0.5"),
        sample.replace("*D_NET *2 0.6", "*D_NET *2 nan"),
    ):
        try:
            parse_spef(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("Fail-open malformed SPEF")
    try:
        effective_cap(a, 1.1)
    except ValueError:
        pass
    else:
        raise AssertionError("Accepted unphysical rho")
    print("V296_COUPLING_ACTIVITY_BOUNDARY_SELFTEST_PASS")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--pairwise", type=Path)
    p.add_argument("--serial", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.pairwise or not args.serial:
        p.error("Provide both frozen ZIP artifacts")
    try:
        result = analyze(args.pairwise, args.serial)
    except (ValueError, OSError, UnicodeError, KeyError, zipfile.BadZipFile) as e:
        result = {"decision": "COUPLING_ACTIVITY_AUDIT_INCOMPLETE", "error": str(e),
                  "source_run": SOURCE_RUN, "physical_gate": "BOTH_INFEASIBLE"}
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
    print(payload)
    if result["decision"] != "COUPLING_ACTIVITY_PROXY_COMPUTED_NOT_PHYSICAL_CLOSURE":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
