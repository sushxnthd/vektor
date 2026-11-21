# V317 routed clock advantage: conditional falsification and electrical-repair budget (2026-11-10 UTC)

Evidence provenance: matched relaxed-geometry OpenROAD artifact from [run 42656831972](https://github.com/sushxnthd/vektor/actions/runs/42656831972), independently inspected in prior audit; this note recomputes consequences without claiming new routing. Existing V296 physical/electrical priority remains unchanged. V287 is historical.

| Quantity | Compact | Pairwise |
|---|---:|---:|
| Prior routed cell area (um^2; different earlier three-way run) | 21314.6 | 21324.7 |
| Latest routed period (ns; run 42656831972) | 2.24 | 2.20 |
| Setup violations | 0 | 0 |
| Hold violations | 0 | 12 |
| Max capacitance violations | 10 | 13 |
| DRC signoff | unverified | unverified |

**Cross-run caveat:** area numbers and clock numbers originate from *different* physical experiments. Their combination below is a conditional illustration, **not** a matched-run PPA result. Both latest routes are electrically illegal; the putative clock advantage cannot be accepted.

Let S = completed work per cycle of pairwise / compact, A = pairwise / compact area, and T = pairwise / compact clock period. The throughput-per-area ratio is exactly R = S/(A*T) under equal work definitions and no additional shared-resource effects. For the previously reported areas A=21324.7/21314.6 = 1.00047385; for the reported clocks T=2.20/2.24=0.98214286. Thus the *hypothetical* no-service-change R=1/(A*T) is approximately 1.0177, but is **invalidated by electrical violations and cross-run comparison**. A 2% materiality gate requires S >= 1.02*A*T, approximately 1.0022 for these illustrative numbers, and also requires *both* candidates to pass all electrical/DRC checks in the same run. The 2% threshold is a research relevance criterion, not a physical signoff standard.

Sensitivity: if pairwise repair adds delta_ns to its period, holding compact at 2.24 ns and both areas unchanged, the S=1 break-even is delta_ns < 2.24/A - 2.20, about 0.03894 ns. A >=2% throughput-per-area improvement at S=1 requires delta_ns <= 2.24/(1.02*A) - 2.20, about -0.00497 ns: **the current illegal 2.20 ns pairwise period would already be too slow to clear the 2% gate without service gain**, even before repair. If compact repair changes period too, all thresholds must be recomputed with matched repaired values; do not hold compact fixed in a claimed final comparison.

Physical decision: preserve negative evidence; repair 10 compact and 13 pairwise max-cap violations plus 12 pairwise hold violations, prove DRC signoff, then compare same-run routed area and period with an issue-width-matched compact alternative. If electrical repair erases the conditional gain or equal-resource scheduling removes service gain, reject V317 rather than continuing proxy-only optimization. No claim of GPU IPC or RTX 5090 equivalence follows from these numbers.
