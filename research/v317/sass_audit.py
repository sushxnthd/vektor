#!/usr/bin/env python3
"""V317: conservative lexical NVIDIA SASS source-operand auditor.

NOT a register-file traffic, bank-conflict, cache-hit, cycle, or throughput model.
Unknown instructions are counted explicitly; no physical-bank mapping is inferred.
Run: python3 research/v317/sass_audit.py --input path/to/disassembly.sass
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

# Explicit, deliberately narrow syntax and semantics allowlists.
DEST_FIRST = frozenset({
    "MOV", "FADD", "FMUL", "FFMA", "DADD", "DMUL", "DFMA",
    "IADD", "IADD3", "IMAD", "LOP3", "SHF", "LEA", "FSEL",
    "PRMT", "BFE", "BFI", "S2R", "LDG", "LDS", "LDC",
    "LDL", "LD",
})
ALL_SOURCE = frozenset({"STG", "STS", "STL", "ST"})
LINE = re.compile(
    r"^\s*/\*(?P<pc>[0-9a-fA-F]+)\*/\s*"
    r"(?:(?P<pred>@!?P\d+)\s+)?"
    r"(?P<opcode>[A-Za-z][A-Za-z0-9_.]*)"
    r"(?:\s+(?P<operands>.*?))?\s*;\s*"
    r"(?:/\*[^*]*\*/\s*)?$"
)
REGISTER = re.compile(r"(?<![A-Za-z0-9_])(?P<reg>R(?:Z|\d+))"
                      r"(?P<reuse>\.reuse)?(?![A-Za-z0-9_])")
PC_PREFIX = re.compile(r"^\s*/\*[0-9a-fA-F]+\*/")
NO_PC_CANDIDATE = re.compile(
    r"^\s*(?:@!?P\d+\s+)?[A-Za-z][A-Za-z0-9_.]*\s+.+;\s*$"
)


@dataclass(frozen=True)
class Parsed:
    pc: str
    opcode: str
    predicate: str | None
    source_registers: tuple[str, ...]
    reuse_hints: tuple[str, ...]
    classification: str


def split_operands(text: str) -> tuple[str, ...]:
    """Split commas outside bracketed address expressions."""
    if not text.strip():
        return ()
    chunks: list[str] = []
    start = 0
    stack: list[str] = []
    pairs = {"]": "[", "}": "{", ")": "("}
    for i, ch in enumerate(text):
        if ch in "[{(":
            stack.append(ch)
        elif ch in "]})":
            if not stack or stack.pop() != pairs[ch]:
                raise ValueError("unbalanced operand delimiter")
        elif ch == "," and not stack:
            chunks.append(text[start:i].strip())
            start = i + 1
    if stack:
        raise ValueError("unbalanced operand delimiter")
    chunks.append(text[start:].strip())
    if any(not x for x in chunks):
        raise ValueError("empty operand")
    return tuple(chunks)


def parse_instruction(line: str) -> Parsed | None:
    m = LINE.fullmatch(line)
    if m is None:
        return None
    opcode = m["opcode"].upper()
    root = opcode.split(".")[0]
    operands = split_operands(m["operands"] or "")
    if root in DEST_FIRST:
        if len(operands) < 2:
            raise ValueError("dest-first opcode missing source operands")
        sources = operands[1:]
        classification = "dest_first"
    elif root in ALL_SOURCE:
        if len(operands) < 2:
            raise ValueError("store missing address/value operands")
        sources = operands
        classification = "all_source"
    else:
        sources = ()
        classification = "unknown"
    tokens = [match for operand in sources for match in REGISTER.finditer(operand)]
    return Parsed(
        pc=m["pc"].lower(), opcode=opcode, predicate=m["pred"],
        source_registers=tuple(x["reg"] for x in tokens if x["reg"] != "RZ"),
        reuse_hints=tuple(x["reg"] for x in tokens
                          if x["reg"] != "RZ" and x["reuse"] is not None),
        classification=classification,
    )


def audit(text: str) -> dict:
    opcode_counts: Counter[str] = Counter()
    unknown_opcodes: Counter[str] = Counter()
    sources: Counter[str] = Counter()
    reuse: Counter[str] = Counter()
    counts: Counter[str] = Counter()
    examples: list[dict] = []
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            counts["blank"] += 1
            continue
        try:
            inst = parse_instruction(line)
        except ValueError as exc:
            counts["unparsed_candidate"] += 1
            if len(examples) < 12:
                examples.append({"line": number, "reason": str(exc),
                                 "text": stripped[:160]})
            continue
        if inst is None:
            if PC_PREFIX.match(line) or NO_PC_CANDIDATE.match(line):
                counts["unparsed_candidate"] += 1
                if len(examples) < 12:
                    examples.append({"line": number, "reason": "unsupported syntax or missing PC",
                                     "text": stripped[:160]})
            else:
                counts["noninstruction"] += 1
            continue
        counts["instructions"] += 1
        opcode_counts[inst.opcode] += 1
        if inst.predicate:
            counts["predicated"] += 1
        if inst.classification == "unknown":
            counts["unknown_semantics"] += 1
            unknown_opcodes[inst.opcode] += 1
            continue
        counts["classified"] += 1
        sources.update(inst.source_registers)
        reuse.update(inst.reuse_hints)
    return {
        "schema": "vektor.v317.sass_lexical_audit.v1",
        "claim_boundary": "static lexical source occurrences only; NOT RF reads, "
                          "RF-cache misses, physical banks, dynamic counts, cycles or GPU speedup",
        "counts": {k: counts[k] for k in (
            "instructions", "classified", "unknown_semantics", "unparsed_candidate",
            "predicated", "noninstruction", "blank")},
        "coverage_fraction": (
            counts["classified"] / counts["instructions"] if counts["instructions"] else None),
        "opcode_counts": dict(sorted(opcode_counts.items())),
        "unknown_opcodes": dict(sorted(unknown_opcodes.items())),
        "source_register_occurrences": dict(sorted(sources.items())),
        "reuse_hint_occurrences": dict(sorted(reuse.items())),
        "source_occurrences_total": sum(sources.values()),
        "reuse_hints_total": sum(reuse.values()),
        "unparsed_examples": examples,
        "physical_bank_map_known": False,
        "reuse_hint_is_cache_hit": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--disassembler", help="Exact disassembler name and version")
    p.add_argument("--target-sm", help="Compiler/disassembler target SM")
    p.add_argument("--binary-sha256", help="SHA256 of compiled binary; user supplied, not verified")
    args = p.parse_args()
    raw = args.input.read_bytes()
    result = audit(raw.decode("utf-8"))
    result["provenance"] = {
        "disassembly_sha256": hashlib.sha256(raw).hexdigest(),
        "disassembler": args.disassembler,
        "target_sm": args.target_sm,
        "binary_sha256_supplied_unverified": args.binary_sha256,
        "metadata_supplied": all((args.disassembler, args.target_sm, args.binary_sha256)),
        "binary_verified": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
