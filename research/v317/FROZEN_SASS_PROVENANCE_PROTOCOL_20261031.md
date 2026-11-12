# V317 preregistered SASS evidence/provenance gate (2026-10-31)

Status: **instrumentation and fidelity screen, not a promoted architecture mechanism**. V316 is retired. Do not reuse older collector speedups as Blackwell throughput evidence. One research branch and one draft PR for this gate.

## Question and required output
Can a small, independently auditable parser convert real NVIDIA SASS disassembly into *lexical source-register occurrence* statistics without silently inventing RF bank mapping, cache hits, dependency timing, dynamic execution counts, or RTX 5090 internals?

## Frozen acceptance criteria (before running fixtures)
1. Accept both `/*pc*/ OP ... ; /*encoding*/` and optional predicated `/*pc*/ @P0 OP ... ;` lines. Skip encoding comments, metadata, labels, and blank lines.
2. Source extraction must exclude destination register for an explicit allowlist of dest-first ALU opcodes, include address-register uses for recognized store instructions, exclude RZ, and treat all other instructions as **unknown**, not as zero demand.
3. Count `.reuse` only as a **compiler hint marker**, never as a guaranteed RF-cache hit or physical-read saving.
4. Unknown opcodes, unsupported formats, absent PC, and noninstruction text must remain visible in coverage/rejection counters. Missing or ambiguous evidence must never be imputed as zero demand.
5. Independent tests: ALU, predicate, duplicate register, RZ, reuse, memory address, unknown opcode, comments, malformed line, and deterministic JSON. Fixture is *synthetic SASS-like syntax* until a provenance-pinned real binary is supplied.
6. CI must execute the tests on a hosted runner. A passed synthetic fixture **does not** establish real SASS parser completeness or GPU performance.
7. Do not promote a hardware candidate or estimate speedup until a real compiled binary, disassembler/tool versions, architecture target, and independently checked disassembly are available. No fabricated bank mapping.

## Kill / revise
If the parser mislabels unknown instructions as known or treats reuse hints as RF hits, reject the instrument. If real disassembly uses unsupported syntax, expand the parser with tests *before* computing statistics. An eventual architecture candidate requires strong modern RF-cache-aware equal-resource baselines, frozen win/no-win and unseen traces, RTL and matched PPA.

Source motivation: Huerta et al., MICRO 2025, DOI:10.1145/3725843.3756041 (studied GPUs; not a claim about exact RTX 5090 internals).
