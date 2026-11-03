#!/usr/bin/env python3
"""V317 paired third-party sm80 SASS listing audit. No GPU performance inference."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.request import urlopen

URLS = {
    "fast": "https://gist.github.com/shunting314/90f35fd6ccc905a9ff3124e1c0a6dfad/raw/dd1b8a74e5ca6b5bddfde09065650371486b0675/fast.sass",
    "slow": "https://gist.github.com/shunting314/157c1a01e8c37bbd8d707ba1b8f038f9/raw/31f9e57dd456ef54b396cfe1b576ed63712bd0e7/slow.sass",
}
EXPECTED_SHA256 = {
    "fast": "987209a727aec2089969abc405a87d9714480f4617749e71f63aaa3b99d6c95f",
    "slow": "9a3f845bcce6e9277201ad7337f250acc9ff12abca6e75df4acefe0e0173bac0",
}
PC = re.compile(r"^\s*/\*([0-9a-fA-F]+)\*/\s*(.*?)\s*;\s*/\*\s*(0x[0-9a-fA-F]+)\s*\*/\s*$")
CONTROL = re.compile(r"^\s*/\*\s*(0x[0-9a-fA-F]+)\s*\*/\s*$")
REGISTER = re.compile(r"(?<![A-Za-z0-9_])R(?:Z|\d+)(?:\.reuse)?(?![A-Za-z0-9_])")

def parse_listing(text: str) -> dict:
    """Independent PC/encoding extraction; not an RF-read or opcode model."""
    if "code for sm_80" not in text or "Function :" not in text:
        raise ValueError("missing sm_80/function provenance header")
    lines = text.splitlines()
    out = {}
    for i, line in enumerate(lines):
        match = PC.fullmatch(line)
        if match is None:
            continue
        pc, instruction, word = match.groups()
        pc = pc.lower()
        if pc in out:
            raise ValueError("duplicate PC " + pc)
        following = CONTROL.fullmatch(lines[i + 1]) if i + 1 < len(lines) else None
        if following is None:
            raise ValueError("missing control word after PC " + pc)
        out[pc] = {"instruction": instruction.strip(), "word": word.lower(),
                   "control": following.group(1).lower()}
    if not out:
        raise ValueError("no PC-prefixed instructions")
    return out

def evaluate(raw: dict) -> dict:
    from research.v317.sass_audit import audit
    text = {k: raw[k].decode("utf-8", errors="strict") for k in URLS}
    maps = {k: parse_listing(text[k]) for k in URLS}
    if set(maps["fast"]) != set(maps["slow"]):
        raise ValueError("different PC sets")
    metrics = {}
    for k in URLS:
        x = audit(text[k])
        n = len(maps[k])
        if x["counts"]["instructions"] != n:
            raise ValueError("PC count disagrees with independent parser")
        if x["counts"]["classified"] + x["counts"]["unknown_semantics"] != n:
            raise ValueError("opcode accounting mismatch")
        digest = hashlib.sha256(raw[k]).hexdigest()
        metrics[k] = {
            "url": URLS[k], "bytes": len(raw[k]), "sha256": digest,
            "matches_frozen_text_sha256": digest == EXPECTED_SHA256[k],
            "instructions": n, "classified": x["counts"]["classified"],
            "unknown_semantics": x["counts"]["unknown_semantics"],
            "unparsed_candidates": x["counts"]["unparsed_candidate"],
            "coverage": x["coverage_fraction"],
            "static_source_occurrences": x["source_occurrences_total"],
            "static_source_per_instruction": x["source_occurrences_total"] / n,
            "reuse_hints": x["reuse_hints_total"],
            "source_register_histogram": x["source_register_occurrences"],
            "unknown_opcode_histogram": x["unknown_opcodes"],
        }
    differences = {"instruction_text": [], "instruction_word": [],
                   "control_word": [], "register_tokens": []}
    for pc in sorted(maps["fast"], key=lambda x: int(x, 16)):
        a, b = maps["fast"][pc], maps["slow"][pc]
        if a["instruction"] != b["instruction"]:
            differences["instruction_text"].append(pc)
        if a["word"] != b["word"]:
            differences["instruction_word"].append(pc)
        if a["control"] != b["control"]:
            differences["control_word"].append(pc)
        if REGISTER.findall(a["instruction"]) != REGISTER.findall(b["instruction"]):
            differences["register_tokens"].append(pc)
    return {
        "schema": "vektor.v317.paired_sass_listing_transfer.v1",
        "protocol": "FROZEN_PAIRED_SASS_LISTING_AUDIT_20261103.md",
        "evidence_tier": "third-party sm80 text; no original binary, toolchain or timings verified",
        "metrics": metrics, "matched_pc_count": len(maps["fast"]),
        "differences_by_pc": differences,
        "lexical_source_histograms_identical": metrics["fast"]["source_register_histogram"] == metrics["slow"]["source_register_histogram"],
        "binary_verified": False, "dynamic_execution_counts_known": False,
        "physical_bank_mapping_known": False, "rf_cache_hits_known": False,
        "gpu_speedup_inference_allowed": False,
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fast", type=Path)
    p.add_argument("--slow", type=Path)
    args = p.parse_args()
    if bool(args.fast) != bool(args.slow):
        p.error("provide both local listings or neither to fetch pinned URLs")
    raw = {}
    for k, url in URLS.items():
        path = getattr(args, k)
        if path:
            raw[k] = path.read_bytes()
        else:
            with urlopen(url, timeout=30) as response:
                raw[k] = response.read(4_000_001)
            if len(raw[k]) > 4_000_000:
                raise ValueError("listing exceeds 4 MB cap")
    print(json.dumps(evaluate(raw), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
