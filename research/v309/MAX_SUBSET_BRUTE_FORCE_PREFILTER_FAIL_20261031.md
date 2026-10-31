# V309 brute-force maximum-subset RTL: frozen prefilter falsification (2026-10-31)

**Decision: KILL the brute-force enumerating RTL implementation** `rtl/vtile/max_subset_arbiter.sv`. Do not route, promote, or claim a GPU gain for it. This does **not** revive V287 or V296, nor establish a new architecture win. The maximum-cardinality admission *policy* remains a research question, not a surviving physical mechanism.

## Source-pinned hosted evidence

- Run: https://github.com/sushxnthd/vektor/actions/runs/41147375323
- Source commit: `e9a2aea446d5c85c8d2df499f3fa042f0bcf6666`
- Preserved raw logs and `summary.json`: https://github.com/sushxnthd/vektor/actions/runs/41147375323/artifacts/13021073462
- Yosys version reported: 0.33 (`2584903a060`).
- Independent Icarus oracle and both frozen motifs: **PASS** (104,976 reduced-bank vectors plus four directed cases, 104,980 total).
- Same-interface generic Yosys synthesis: **PASS** for both designs, with `check` reporting zero problems for candidate.
- Frozen 2.0x generic-cell prefilter: **FAIL**, deliberately causing the workflow's nonzero exit.

| Metric | Existing serial greedy | Exact 16-subset enumeration | Candidate / baseline |
|---|---:|---:|---:|
| Generic mapped cells | 1,321 | 3,802 | **2.8781226344x** |
| Longest topological path (generic gate edges) | 49 | 54 | 1.1020x |

The 3,802 cells exceed the predeclared ceiling of 2,642 by **1,160 cells** (43.91% above the allowed ceiling). The result is a *generic logic proxy*, not standard-cell area, post-route delay, setup/hold closure, or electrical signoff. The longer topological path is an additional warning, not a calibrated timing estimate.

## Why this is a scientific rejection, not CI breakage

The testbench demonstrated that the combinational policy implements the independent exact oracle on its covered input domain and delivers the frozen 3-versus-2 admission motif while preserving the 4-versus-4 no-win motif. But a functional advantage is irrelevant if the circuit is unaffordable. The frozen area ceiling was specified *before* the hosted outcome and failed. The job intentionally exited with `FROZEN_AREA_PREFILTER_FAIL`, then successfully uploaded complete logs. No post-hoc relaxation of the 2.0x threshold is permitted.

## Mechanistic diagnosis and next falsification

The enumerator replicates 16-bank demand loops across 16 candidate masks and performs repeated count/compare logic. A **factored exact-policy implementation** is a possible *implementation-level* follow-up, not evidence that this rejected RTL survives. It should exploit the two-read-port condition: a subset is legal exactly when no three of its selected operand occurrences address the same bank. Pair and triple feasibility can be shared across the 4 request slots; a four-request subset is feasible iff each of its four three-request subsets is feasible. Freeze the same input/port contract, exact smallest-numeric-mask tie break, independent oracle, and **unchanged 2.0x cell ceiling**. Reject any factored RTL that fails functionality or generic synthesis; only if it passes may it proceed to matched standard-cell timing, wiring, capacitance, power proxy, fairness, and workload-level throughput.

**Evidence tier:** RTL functional simulation + generic mapped synthesis + negative area prefilter. No standard-cell PPA, tile-level gain, or RTX 5090 equivalence.
