# V317 source-demand identifiability falsification (2026-10-31)

Status: **negative inference result, not a GPU mechanism or performance result**.

## Prospective adversarial checks

The source auditor reports explicitly written register tokens. A second independent fail-closed gate was added before anyone can interpret those counts as physical register-file traffic. The following cases were frozen as unit tests before hosted execution:

| Input | Lexical tokens counted | What remains unidentifiable |
| --- | ---: | --- |
| `IADD3 R0, R1, R2, R3` | 3 | physical RF reads, reuse-cache behavior, bank mapping, dynamic frequency |
| `STG.E.128 [R2], R4` | 2 | semantic register-tuple width of the store data operand |
| `DFMA R0, R2, R4, R6` | 3 | physical register width of double-precision source operands |
| `MOV R0, R1` plus unknown `ATOM.E.ADD` | 1 classified | unclassified instruction demand |
| predicated `FFMA` | 3 | whether the instruction executes dynamically |
| `FFMA R1, R2.reuse, R3, R4` | 3 | whether the compiler reuse hint produces a physical cache hit |

These are **synthetic SASS-like adversarial inputs**, not hardware traces. Wide-register examples are deliberately conservative hazard flags, not a complete ISA specification.

## Exact inference boundary

Even when every instruction is lexically classified, a static instruction listing does not determine dynamic execution counts, register-cache hits, physical bank mapping, port scheduling or register-file read traffic. Consequently, the new checker emits **null** for physical-read bounds, bank conflicts and GPU throughput, and sets physical-performance eligibility to false. It never turns unknown instructions into zero reads.

This falsifies the tempting inference that 100% static lexical coverage suffices for physical demand estimation. The result is an epistemic limitation, not a discovery of new GPU microarchitecture.

## Verification

Source-pinned hosted [V317 workflow #41210657978](https://github.com/sushxnthd/vektor/actions/runs/41210657978) passed **18/18** tests at commit `10cc07a57390264b0b4547f1b1a66f87e6c5db01`. The original nine lexical tests remain passing; nine additional tests cover widened stores, double-precision sources, unknown and malformed instructions, predication, reuse, provenance and empty input.

The hosted workflow currently uploads the original lexical JSON artifact; it does **not** claim a hardware-derived demand artifact. The additional gate is exercised by the independent tests.

## Required next scientific step

1. Obtain a reproducibly compiled GPU kernel and provenance-pinned disassembly with compiler, disassembler, target SM and binary hashes. Do not infer hardware behavior from a text fixture.
2. Measure or bound dynamic instruction weights and reuse-cache behavior independently, or carry uncertainty intervals forward.
3. Build a modern register-cache-aware matched baseline and a workload-level resource budget. Only promote a mechanism after a preregistered predicted-win and no-win regime survives that baseline.
4. Any promoted mechanism still requires RTL, matched PPA, electrical checks, power proxies and unseen workload validation. No RTX 5090 equivalence claim is supported.

V317 remains an evidence gate, not an active architecture mechanism. V287/V296 historical work is not reopened. Kernellum PR #119 is unchanged.
