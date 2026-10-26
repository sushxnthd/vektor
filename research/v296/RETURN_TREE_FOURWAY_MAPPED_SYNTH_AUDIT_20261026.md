# V296 balanced RF-return tree: hosted four-way mapped synthesis audit (2026-10-26)

## Evidence and scope

The frozen four-way synthesis job in [Actions run 40244774412](https://github.com/sushxnthd/vektor/actions/runs/40244774412) completed successfully. The mapped artifact is **12618038449**, ZIP SHA-256 `0d88dfab95f6d01fb1b6e0798af7f815bee148aef0da632e12a1558d546b9df1`. The library is Nangate45 typical (SHA-256 `8d540a4d4cf6d09d27c87ad067857a9c0c2eeb023ab7a56e058cd3113db4e9b1`), synthesized with Yosys 0.9 (git 1979e0b). Both RTL source hashes are recorded in `RETURN_TREE_FOURWAY_MAPPED_AUDIT_RESULTS_20261026.json`. The pre-evaluation protocol is `RETURN_TREE_INTEGRATED_REPAIR_PREREG_20261026.md`; the original implementations were not modified.

An independent Python parser `return_tree_mapped_audit.py` verifies all four hosted log SHA-256 digests, the technology-library hash, the manifest, unique area/path records, exact module names, and complete longest-path node enumerations. Local audit passed; a one-digit area-log mutation and technology-library corruption were both rejected. This is post-hoc independent artifact checking, **not** a prospectively frozen area prediction.

## Four-way mapped results

| Implementation | Mapped standard-cell area (µm²) | Yosys `ltp -noff` edges |
|---|---:|---:|
| Original V296 pairwise | 9,620.954 | 268 |
| Original serial one-hot | 10,029.264 | 262 |
| Balanced-return V296 pairwise | 9,286.592 | 235 |
| Balanced-return serial one-hot | 9,844.926 | 279 |

- **V296 implementation intervention:** mapped area decreases **3.475%** and graph depth decreases **12.313%** (268 → 235).
- **Fair serial control receives the identical intervention:** mapped area decreases **1.838%**, but graph depth **increases 6.489%** (262 → 279). Thus the balanced return is not a universally improving transformation.
- **Both balanced-return implementations:** V296 maps to **5.671% less area** and **15.771% fewer graph edges** than serial one-hot. This is not an equal-consumed-tile-area or physical-timing comparison.

The Yosys longest graph path for both pairwise implementations starts at `src1_bank_by_wave[127]`; the serial versions start at `wave_valid[31]`. The endpoint bit also changes across implementations. The graph path is a **structural proxy**, not a timing arc with mapped cell delay, extracted interconnect RC, fanout, clock uncertainty, or setup/hold constraints. Do not equate 235 versus 279 edges with frequency improvement. A mapped-area reduction is not a measured power reduction.

## Predictive performance boundary and falsifier

Formal SAT evidence establishes identical grant semantics for V296 and serial one-hot; the balanced return changes shared RF-return implementation only. For a common prospective traffic distribution, let `λ(p,ρ,c,κ)` be useful admissions per eligible cycle, depending on validity `p`, bank/operand overlap `ρ`, cross-slot correlation `c`, and bank-port pressure `κ`. Let `o` be occupancy availability, `h` control overhead, `f_i` **independently physically feasible** frequency, `d` bytes/admission, and `β` external bandwidth. The throughput model is

`T_i = min[f_i λ(p,ρ,c,κ) o (1-h), β/d]`.

Because the admission function is identical, **at matched clock and resources `T_V296/T_serial - 1 = 0`** under this model. For `A = λ o(1-h)` shared across contestants, a clock-derived positive gain requires both `f_V296 > f_serial` and `β/d > A f_serial`. If `β/d <= A f_serial`, predict **no useful-throughput gain** even with a faster V296 clock. If both are compute-limited, predicted gain is `f_V296/f_serial - 1`. This is an explicitly conditional analytical boundary, not a newly validated architecture speedup. Correlation-aware `λ` and unseen workloads remain required.

The **frozen predicted-win regime** remains high-occupancy, non-bandwidth-saturated banked-RF traffic *if* matched physically feasible clocks differ. The **frozen no-win regime** remains external-bandwidth saturation. Do not change these after seeing physical results.

## Decision and next gate

The topology survives the **mapped synthesis hypothesis** for V296 and passes the previously completed hosted four-way RTL test. **It has not passed physicality.** The paired detailed-route OpenRCX jobs in the same Actions run were still executing when this audit was written. Require both contestants to satisfy frozen 3.5 ns clock, +50 ps setup margin, nonnegative hold, zero capacitance/slew violations, identical 2× RC sensitivity, and then enforce equal-consumed-area accounting. If either fails, no integrated feasible speedup claim. If both pass but the independently optimized serial control erases the frequency/area advantage, kill the performance claim.

V296 remains the sole provisional architecture mechanism; V287 stays retired. No production GPU, measured energy benefit, or RTX-5090-equivalence claim follows from these results. Kernellum PR #119 and its prospective holdouts are untouched.
