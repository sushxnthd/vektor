#!/usr/bin/env python3
"""Fail-closed external H200 trace acquisition budget gate, metadata only.

Consumes GitHub release API JSON, NOT a trace, manifest or performance counter.
The minimum byte cost for k distinct workload families is exact: choose each
family's cheapest complete configuration, then the k cheapest families.
"""
import argparse
import json
import re
import sys
from collections import defaultdict

RELEASE_ID = 418693044
TAG = "v2.0.1"
PATTERN = re.compile(r"^(H200)__(.+?)__(.+?)\.tar\.part(\d{3})$")


def analyze(release, budget_mib=512, family_count=3):
    if release.get("id") != RELEASE_ID or release.get("tag_name") != TAG:
        raise ValueError("unexpected release identity")
    if release.get("draft") or release.get("prerelease"):
        raise ValueError("unqualified release")
    if not isinstance(budget_mib, int) or budget_mib < 1 or family_count < 1:
        raise ValueError("invalid acquisition constraints")
    groups = defaultdict(list)
    meta = set()
    for a in release.get("assets", []):
        name = a.get("name", "")
        if name in ("README.md", "manifest.json"):
            if name in meta:
                raise ValueError("duplicate metadata asset")
            meta.add(name)
            continue
        match = PATTERN.fullmatch(name)
        if not match:
            raise ValueError(f"unknown release asset: {name}")
        gpu, workload, args, index = match.groups()
        if not isinstance(a.get("size"), int) or a["size"] <= 0:
            raise ValueError("invalid asset size")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", a.get("digest", "")):
            raise ValueError("missing/invalid asset digest")
        groups[(gpu, workload, args)].append((int(index), a["size"]))
    if meta != {"README.md", "manifest.json"} or not groups:
        raise ValueError("release metadata incomplete")
    configs = []
    for (gpu, workload, args), parts in groups.items():
        indexes = sorted(p[0] for p in parts)
        if indexes != list(range(len(parts))):
            raise ValueError(f"missing or duplicate trace part: {workload}/{args}")
        configs.append({"gpu": gpu, "workload": workload, "args": args,
                        "bytes": sum(p[1] for p in parts), "parts": len(parts)})
    configs.sort(key=lambda x: (x["bytes"], x["workload"], x["args"]))
    selected, seen = [], set()
    for c in configs:
        if c["workload"] not in seen:
            seen.add(c["workload"])
            selected.append(c)
            if len(selected) == family_count:
                break
    if len(selected) != family_count:
        raise ValueError("insufficient independent workload families")
    budget = budget_mib * (1 << 20)
    minimum = sum(x["bytes"] for x in selected)
    return {"evidence_tier": "release_asset_metadata_only_no_trace_download",
            "release_id": RELEASE_ID, "tag": TAG,
            "configurations": len(configs),
            "parts": sum(c["parts"] for c in configs),
            "total_release_trace_bytes": sum(c["bytes"] for c in configs),
            "minimum_single_configuration_bytes": configs[0]["bytes"],
            "minimum_distinct_family_bytes": minimum,
            "required_families": family_count, "budget_mib": budget_mib,
            "within_budget": minimum <= budget,
            "any_single_configuration_within_budget": configs[0]["bytes"] <= budget,
            "selected_cheapest_distinct_families": selected,
            "qualification": "BLOCKED_BY_BYTE_BUDGET" if minimum > budget
                             else "SIZE_ONLY_ELIGIBLE_NOT_VALIDATED"}


def selftest():
    import copy
    import itertools
    def asset(w, arg, part, size):
        return {"name": f"H200__{w}__{arg}.tar.part{part:03d}",
                "size": size, "digest": "sha256:" + "a" * 64}
    base = {"id": RELEASE_ID, "tag_name": TAG, "draft": False,
            "prerelease": False, "assets": [
                {"name": "README.md"}, {"name": "manifest.json"},
                asset("A", "x", 0, 10), asset("A", "x", 1, 20),
                asset("A", "y", 0, 8), asset("B", "x", 0, 40),
                asset("C", "x", 0, 15)]}
    r = analyze(base, 1, 3)
    assert r["minimum_distinct_family_bytes"] == 63
    configs = [("A", 30), ("A", 8), ("B", 40), ("C", 15)]
    brute = min(sum(s for _, s in combo)
                for combo in itertools.combinations(configs, 3)
                if len({w for w, _ in combo}) == 3)
    assert brute == r["minimum_distinct_family_bytes"]
    mutants = []
    x = copy.deepcopy(base); x["id"] += 1; mutants.append(x)
    x = copy.deepcopy(base); x["assets"][2]["digest"] = "sha256:bad"; mutants.append(x)
    x = copy.deepcopy(base); x["assets"][3]["name"] = x["assets"][2]["name"]; mutants.append(x)
    x = copy.deepcopy(base); x["assets"][3]["name"] = "H200__A__x.tar.part002"; mutants.append(x)
    x = copy.deepcopy(base); x["assets"][2]["size"] = -1; mutants.append(x)
    x = copy.deepcopy(base); x["assets"].pop(0); mutants.append(x)
    for x in mutants:
        try:
            analyze(x)
        except ValueError:
            pass
        else:
            raise AssertionError("fail-closed mutation escaped")
    print("PASS: exact three-family selection and six fail-closed mutations")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("release_json", nargs="?", help="GitHub REST release JSON")
    p.add_argument("--budget-mib", type=int, default=512)
    p.add_argument("--families", type=int, default=3)
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    if args.selftest:
        selftest()
        if not args.release_json:
            return
    if not args.release_json:
        p.error("release_json required except for --selftest")
    with open(args.release_json, encoding="utf-8") as f:
        release = json.load(f)
    print(json.dumps(analyze(release, args.budget_mib, args.families), indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError) as e:
        print(f"FAIL CLOSED: {e}", file=sys.stderr)
        sys.exit(2)
