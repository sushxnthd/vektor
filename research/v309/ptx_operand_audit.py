#!/usr/bin/env python3
"""V309: fail-closed static PTX operand audit. Not a SASS/GPU performance model."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
import re
import urllib.request

SOURCES = {
    "triton_gelu": {
        "url": "https://raw.githubusercontent.com/stanford-cs336/lectures/de53a9f979a6ee35f7d13a5e1aadee5ea1afc58e/var/triton_gelu-ptx.txt",
        "blob": "09d8fce9016b6fe0e36e31ac3a47fc9feddee206",
        "target": "sm_100a",
    },
    "atomic_reduction": {
        "url": "https://raw.githubusercontent.com/parallel101/course/aa7715d26b55bda8ad7a9444a923c916eda30b7f/08/07_atomic/04/a.ptx",
        "blob": "17873acef2f5137137ca0c4967bd696b97e31c01",
        "target": "sm_52",
    },
}
DATA = re.compile(r"%(?:r|rd|f|fd|h|b|u|v)\d+\b")
PRED = re.compile(r"%p\d+\b")
TOKEN = re.compile(r"%[A-Za-z_][A-Za-z_0-9.]*")
PREFIXES = {
    "ld", "st", "mov", "shl", "shr", "and", "or", "xor", "not", "setp",
    "mul", "add", "sub", "fma", "ex2", "div", "cvta", "mad", "bra",
    "ret", "atom", "red", "cvt", "max", "min", "selp", "neg", "abs",
    "rem", "rcp", "sqrt", "lg2", "sin", "cos", "bar", "prmt", "lop3",
    "shf", "set", "slct", "vote", "activemask", "popc", "bfind",
    "clz", "brev", "cnot", "bfe", "bfi", "sad", "vadd", "vsub",
    "wmma", "mma", "cp", "prefetch", "membar", "trap", "exit",
}
NO_DEST = {"st", "red", "bra", "ret", "bar", "prefetch", "membar", "trap", "exit", "cp"}
MEMORY = {"ld", "st", "atom", "red", "prefetch", "cp"}
CONTROL = {"bra", "ret", "bar", "trap", "exit", "membar"}


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def split_operands(s: str) -> list[str]:
    """Split top-level operands, preserving vector register braces."""
    result, buf, braces, brackets = [], [], 0, 0
    for ch in s:
        if ch == "{":
            braces += 1
        elif ch == "}":
            braces -= 1
        elif ch == "[":
            brackets += 1
        elif ch == "]":
            brackets -= 1
        if braces < 0 or brackets < 0:
            raise ValueError("unbalanced operand grouping")
        if ch == "," and braces == 0 and brackets == 0:
            result.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if braces or brackets:
        raise ValueError("unbalanced operand grouping")
    result.append("".join(buf).strip())
    return result


def parse_ptx(source: str) -> dict:
    counts = Counter()
    opcodes = Counter()
    inside = False
    saw_entry = False
    awaiting_brace = False
    entries = 0
    for line_no, raw in enumerate(source.splitlines(), 1):
        line = raw.split("//", 1)[0].strip()
        if not line:
            continue
        if ".entry " in line and not inside:
            awaiting_brace = True
            saw_entry = True
            entries += 1
            continue
        if awaiting_brace:
            if line == "{":
                inside = True
                awaiting_brace = False
            continue
        if not inside:
            continue
        if line == "}":
            inside = False
            continue
        if line.startswith((".", "$", "//")) or line.endswith(":") or line in ("{",):
            continue
        if ";" not in line:
            raise ValueError(f"line {line_no}: unterminated instruction: {line[:100]}")
        if line.count(";") != 1 or not line.endswith(";"):
            raise ValueError(f"line {line_no}: unexpected instruction format")
        body = line[:-1].strip()
        predicate = ""
        if body.startswith("@"):
            match = re.match(r"@(!?%p\d+)\s+", body)
            if not match:
                raise ValueError(f"line {line_no}: unsupported predicate")
            predicate = match.group(1)
            body = body[match.end():]
        match = re.fullmatch(r"([A-Za-z][\w.]*)\s*(.*)", body)
        if not match:
            raise ValueError(f"line {line_no}: invalid instruction")
        opcode, operand_text = match.groups()
        prefix = opcode.split(".")[0]
        if prefix not in PREFIXES:
            raise ValueError(f"line {line_no}: unsupported opcode {opcode}")
        operands = split_operands(operand_text) if operand_text else []
        if prefix not in NO_DEST and not operands:
            raise ValueError(f"line {line_no}: missing destination")
        sources = operands if prefix in NO_DEST else operands[1:]
        src_text = ",".join(sources)
        reads = DATA.findall(src_text)
        pred_reads = PRED.findall(src_text) + ([predicate.lstrip("!")] if predicate else [])
        all_tokens = TOKEN.findall(src_text)
        # Only data/predicate registers are counted. PTX special registers
        # such as %tid.x and %ctaid.x do not imply register-file reads.
        unknown = [x for x in all_tokens if not (DATA.fullmatch(x) or PRED.fullmatch(x))
                   and not re.fullmatch(r"%[A-Za-z_][A-Za-z_0-9.]*", x)]
        if unknown:
            raise ValueError(f"line {line_no}: unknown register token {unknown}")
        counts["instructions"] += 1
        counts["data_source_occurrences"] += len(reads)
        counts["unique_data_sources_per_instruction"] += len(set(reads))
        counts["intra_instruction_duplicate_reads"] += len(reads) - len(set(reads))
        counts["predicate_source_occurrences"] += len(pred_reads)
        counts["predicated_instructions"] += bool(predicate)
        counts["memory_instructions"] += prefix in MEMORY
        counts["control_instructions"] += prefix in CONTROL
        counts["zero_data_source_instructions"] += not reads
        opcodes[prefix] += 1
    if not saw_entry or entries == 0 or counts["instructions"] == 0:
        raise ValueError("no PTX entry/instructions found")
    if awaiting_brace or inside:
        raise ValueError("unterminated .entry body")
    n = counts["instructions"]
    unique = counts["unique_data_sources_per_instruction"]
    out = dict(sorted(counts.items()))
    out["entry_count"] = entries
    out["opcode_counts"] = dict(sorted(opcodes.items()))
    out["mean_unique_data_sources"] = round(unique / n, 6)
    out["duplicate_read_fraction_of_occurrences"] = round(
        counts["intra_instruction_duplicate_reads"] / max(1, counts["data_source_occurrences"]), 6
    )
    out["optimistic_rf_service_lower_bound_cycles"] = {
        f"{b}banks_{p}port": math.ceil(unique / (b * p))
        for b, p in [(2, 1), (4, 1), (8, 1)]
    }
    return out


def selftest() -> dict:
    body = """
.visible .entry test()
{
.reg .b32 %r<10>;
add.u32 %r1, %r2, %r2;
@%p1 st.global.v4.b32 [ %rd1 ], { %r1, %r2, %r3, %r4 };
ld.global.v4.b32 { %r1, %r2 }, [ %rd1 ];
mov.u32 %r1, %tid.x;
fma.rn.f32 %f1, %f2, %f2, %f3;
ret;
}
"""
    x = parse_ptx(body)
    assert x["instructions"] == 6, x
    assert x["data_source_occurrences"] == 11, x
    assert x["unique_data_sources_per_instruction"] == 9, x
    assert x["intra_instruction_duplicate_reads"] == 2, x
    assert x["predicated_instructions"] == 1, x
    assert x["predicate_source_occurrences"] == 1, x
    assert x["optimistic_rf_service_lower_bound_cycles"]["2banks_1port"] == 5, x
    # Mutant control: removing operand delimiters must not silently pass.
    for bad in [body.replace("add.u32 %r1, %r2, %r2;", "add.u32 %r1, %r2, %r2"),
                body.replace("fma.rn.f32", "unknown_op.f32"),
                body.replace("[ %rd1 ]", "[ %rd1 }")]:
        try:
            parse_ptx(bad)
        except ValueError:
            continue
        raise AssertionError("malformed/mutated PTX escaped fail-closed parser")
    return {"selftest": "pass", "mutants_detected": 3}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--external", action="store_true")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    if not args.selftest and not args.external:
        parser.error("select --selftest and/or --external")
    report = {"tier": "static_PTX_only_no_SASS_or_runtime"}
    if args.selftest:
        report["tests"] = selftest()
    if args.external:
        report["sources"] = {}
        for name, spec in SOURCES.items():
            with urllib.request.urlopen(spec["url"], timeout=30) as response:
                raw = response.read()
            sha = git_blob_sha(raw)
            if sha != spec["blob"]:
                raise ValueError(f"{name}: Git blob mismatch {sha} != {spec['blob']}")
            metrics = parse_ptx(raw.decode("utf-8"))
            report["sources"][name] = {
                "url": spec["url"], "git_blob": sha, "target": spec["target"],
                "metrics": metrics,
            }
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(encoded, end="")
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(encoded)


if __name__ == "__main__":
    main()
