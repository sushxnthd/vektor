# V309: frozen stronger equal-resource greedy baseline (2026-10-31)

**Status: preregistered before the optimized-greedy RTL synthesis result.** One active mechanism remains the four-slot exact maximum-cardinality bank-admission policy, implemented by `vektor_v309_factored_subset_arbiter`. This document adds a **stronger implementation of the incumbent greedy policy** as a control, not a second candidate mechanism. V287 remains retired; the failed V296 extracted-RC gate is not overridden.

## Prior results disclosed before this preregistration

The existing source-pinned hosted V309 prefilter run #41155714598 passed 109,076 independent RTL-oracle cases. Generic Yosys synthesis reported 1,321 cells / 49 logic edges for the original serial greedy, 3,802 / 54 for the killed enumerating exact-max RTL, and 331 / 18 for the factored exact-max RTL. Both prospective synthetic admission holdouts passed (uniform16 1.000994x, hot3 1.042661x). These **are not physical area, clock speed, energy, or workload speedup**.

## Motivation and stronger control

The original `vektor_rf_bank_arbiter` uses a 16-bank shifting and state-vector update scheme. A combinational, pairwise-comparator implementation of **the same greedy decision function** may be much cheaper and faster. Comparing only against the unoptimized incumbent could therefore falsely credit the new maximum-cardinality *policy* for a better RTL *implementation*.

Construct `vektor_v309_compact_greedy_arbiter` using explicit equality comparisons of the eight operand bank IDs, two reads per request, pairwise and three-request legality predicates, and priority-ordered greedy admission. It must emit exactly the original greedy four-bit grant mask on all test inputs. It must not change read ports, bank count, number of request slots, input or output latency, or priority.

## Frozen verification and stop rules

1. Add compact-greedy to the independent Icarus testbench; compare its exact four-bit mask against the original greedy in **all 104,976 reduced-bank vectors**, the four directed controls, and the **4,096 full-bank vectors** (109,076 cases total). Reject any mismatch. Keep independent per-bank oracle for the factored maximum-cardinality candidate and all port-safety checks.
2. Run matched generic Yosys `synth; stat; ltp -noff` on original greedy, compact greedy, killed enumerator and factored exact-max. Preserve complete source/tool/log evidence. Report cell counts, generic logic depth, and factored-to-compact cell ratio.
3. The previously frozen brute-force kill (ratio >2 relative to original greedy) must still reproduce. **New stronger baseline stop rule:** if factored exact-max exceeds **2.0x the compact greedy's generic mapped cells**, kill the factored implementation even if it beats the original greedy. A passing ratio only authorizes standard-cell synthesis, physical timing and electrical validation.
4. Freeze predicted win motif (greedy 2, exact-max 3), no-win motif (both 4), and the previously published uniform16 and hot3 held-out regimes unchanged. Do not tune thresholds after results.
5. Generic mapped cell count and longest logic path are proxies, not standard-cell area or extracted-RC timing. Even if the stronger control passes, no performance/energy gain is established without matched standard-cell timing, placement, wire/load sensitivity, and queue/occupancy/bandwidth experiments.

## Independence and claim boundary

The RTL equality checker uses the unchanged independent per-bank reference oracle and original greedy implementation; the compact baseline's own internal comparator logic is not used as the reference. A matched-clock issue-throughput advantage is bounded by measured conflict-loss frequency and any control/occupancy/port bottlenecks. Synthetic issue ratios cannot be multiplied into GPU speedups. Preserve negative outcomes; no branch change, merge, force push, or new active mechanism.
