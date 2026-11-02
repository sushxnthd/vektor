# Frozen output-port ceiling theorem and prospective transfer (2026-11-02)

## Scope and non-promotion
V317's physical tile-area claim remains **killed** against compact greedy. This is a necessary-boundary falsification of proposed bank-port scheduling headroom, **not** a new active architecture or a positive GPU performance claim. Continue existing branch `research/v317-sass-provenance-gate` and draft PR #34 only. No merge, new branch, or relaxation of prior gates.

## Model
Four age-ordered valid requests. Each requires two independently consumed bank reads (including same-bank operands), with 2 read ports per bank. A greedy scheduler scans all four requests in age order, admitting each if feasible. A head-preserving optimum enumerates feasible subsets containing request 0. At output width K, instantaneous service is min(K, admitted count). All four requests are valid, and request 0 is individually feasible. This is a combinational bound only: no queues, memory coalescing, RTL timing, starvation proof or GPU IPC.

## Preregistered theorem
For **any number of banks**, any independently feasible requests and any downward-closed joint resource-feasibility relation, a head-preserving maximum-cardinality scheduler has **exactly zero** service advantage over age-greedy when output width K<=2. Proof sketch: greedy always admits request 0. If greedy admits another, both reach K=2. Otherwise, greedy's scan establishes that no other request can be jointly admitted with request 0; a head-preserving feasible subset can contain at most one request. The K=1 case is trivial. Any counterexample falsifies either this proof or the implementation.

For K>=3 the exact ratio identity is
`R_K = 1 + sum_t (min(K,H_t)-min(K,G_t)) / sum_t min(K,G_t)`.
Positive gains require at least one case with G_t<K, and cannot be inferred from unrestricted maximum-cardinality oracles. We do not assume a universal one-grant difference beyond the tested four-slot model.

## Prospective predictions, frozen before running
1. K=2: ratio exactly 1.000000 for uniform16, uniform4, hot65_16, samebank70_16, and **all 65,536** four-bank operand tuples. Tolerance 1e-12.
2. K=3: uniform16 and hot65_16 each <1.02 (no material gain). A ratio >=1.02 falsifies the forecast.
3. K=4: uniform4 >1.01 (small predicted-win *instantaneous service* regime), and hot65_16 <1.02 (no material gain). A miss falsifies the corresponding prediction.
4. Across K=2,3,4: each scenario's ratio is nondecreasing with K. If not, retain counterexample (not assumed theorem).
5. Independent recursive checker must match exhaustive B=2 and B=4 totals for each K, plus independent random holdouts.

## Prospective evaluation
Independent seeds 20261103, 20261107, 20261111; 8,000 four-request batches per seed per scenario. Scenarios: uniform16; uniform4; hot65_16 (P(bank0)=0.65, remaining uniformly 1..15); samebank70_16 (second operand equals first with probability 0.70, otherwise independent uniform). Use identical batches across K=2,3,4. Report raw greedy/head totals, ratios, gain-event probability, and output-ceiling saturation probability. Also enumerate B=2 and B=4 exactly. Separate checker must not import the primary evaluator.

## Decision and evidence tier
If K=2 theorem holds, close K=2 head-preserving scheduling as a source of throughput advantage, regardless of hot-bank skew. If K=4 uniform4 wins, label it only a synthetic instantaneous bound and demand finite-buffer bounded-wait implementation, strong equal-resource RTL and electrical legality before promoting anything. Prior V317 electrical/area failures remain binding. Preserve all negative results, even if unexpected.
