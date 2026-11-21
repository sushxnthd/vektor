# V317 prospective S/B scaling falsification protocol (2026-11-01)

## Scope and noninterference
One existing V317 branch and draft PR #34. The pairwise bank-credit implementation is an RTL cost optimization, not a new scheduler. V287 and V296 are historical, and V317 register forwarding and exact-cardinality selection remain rejected. This is a **new, prospective scaling test** of the only currently useful source-equivalent arbiter optimization. No new architecture mechanism is promoted.

## Frozen question and predictions
For S in {2,4,8} request slots and B in {4,16,64} banks, each granted request consumes two physical reads and each bank supports two reads per cycle. The candidate is pairwise comparison of previously granted operands. The strong alternative is a bank-mask implementation with identical priority and identical ports. Parameterization must not change decisions.

P1 (functional): independent operand-count oracle, exhaustive S=2 B=4 vectors (all valid masks and all operand choices), and 2,048 deterministic random vectors per configuration, with all-zero and full-contention directed cases. Any mismatch kills the optimization.
P2 (cost): pairwise should use fewer generic cells at S=4,B=16; across fixed S=4, increasing B from 4 to 64 should not reduce the pairwise advantage relative to the bank-mask implementation. Report counterexamples without tuning.
P3 (crossover): at S=8,B=4, pairwise may lose its generic-cell advantage due to O(S^2 log B) comparisons. This is an exploratory boundary prediction, not a guaranteed positive result.
P4 (service): at equal clock, ports, issue slots and requests, both implementations must produce identical grants and thus identical service. There is no throughput claim.
P5 (physical): Yosys generic-cell counts and logic levels are **not** mapped standard-cell area or routed delay. Any claimed physical win remains blocked pending matched Liberty mapping, wire/load/clock analysis and electrical checks.

## Precommitted analysis
Measure generic cell count, flip-flops, logic depth and maximum net sink fanout for both implementations under the same Yosys version and synthesis commands. Emit machine-readable per-configuration records and mark whether each frozen prediction survived. Derive only a conditional scaling boundary from the nine observed points, without extrapolating to tile performance or RTX 5090 equivalence. The exact source commit, negative results and logs must be preserved.

## Run sequence
1. Commit this protocol before writing implementation or collecting results.
2. Implement independent parameterized RTL and oracle testbench.
3. Run local independent algorithmic checks and hosted RTL/synthesis with reproducible scripts.
4. Report source-pinned findings and whether a real matched physical gate remains unmet.
