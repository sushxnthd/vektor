# V317 finite-FIFO age-head transfer: constructed predicted win falsified (2026-11-02)

## Evidence order and decision
The prospective protocol [FROZEN_FINITE_AGE_HEAD_QUEUE_GATE_20261102.md](FROZEN_FINITE_AGE_HEAD_QUEUE_GATE_20261102.md) was committed at `4af102ab` **before running the evaluator**. Evaluator and independent checker were committed at `ad52ebcf` and `d0e6ca3b`. Three frozen seeds (42011, 42013, 42017), 3,000 warmup and 12,000 measured cycles/seed, five workloads, same offered traces, 8-entry on-chip FIFO, four-request scheduling window, two reads/request, two read ports/bank. The oldest request must be served every nonempty cycle. The upstream workload source retains blocked requests, **outside** the modeled on-chip FIFO. This is an optimistic synthetic upper bound, not GPU IPC.

**The preregistered constructed predicted-win regime failed.** The first structured four-request snapshot allows 3 head-preserving grants versus 2 greedy grants, but its steady-state finite-FIFO throughput is exactly 2.0000 requests/cycle for **both**. No threshold retuning, new mechanism promotion or revival of the killed V317 physical-area claim.

## Prospective results

| Regime | Frozen forecast | Greedy completed (3 seeds) | Head-optimal completed | Ratio | Gate |
|---|---|---:|---:|---:|---|
| Uniform 16 banks, K=4, 4 offers/cycle | no material win (<1.02) | 137,372 | 137,385 | **1.000095x** | PASS |
| 65%-hot bank, K=4, 4 offers/cycle | no material win (<1.02) | 54,231 | 54,231 | **1.000000x** | PASS |
| Repeated constructed four-bank pattern, K=4 | predicted win (>=1.02) | 72,000 | 72,000 | **1.000000x** | **FALSIFIED** |
| Same constructed pattern, K=2 | exact no-win | 72,000 | 72,000 | **1.000000x** | PASS |
| Uniform 16 banks, K=4, 1 offer/cycle | exact no-win | 36,000 | 36,000 | **1.000000x** | PASS |

The structured pattern is `[(0,0),(1,1),(1,2),(1,2)]`, repeated. It was selected and frozen because its *first snapshot* has greedy 2 and head-preserving optimum 3. It was **not** selected after observing queue results. The positive forecast was wrong. In the uniform16 case the challenger completes only 13 more requests over 36,000 measured cycles (approximately +0.00946%). In the hot65 case both policies complete exactly the same number in every seed.

The maximum on-chip waiting times were respectively 3, 7, 4, 3 and 0 cycles for the challenger; its p99 on-chip wait never exceeded greedy in these tests. This does **not** imply bounded end-to-end latency under overloaded offered traffic: the modeled external source backlog grows substantially, and the hot65 first seed has p99 offered-to-completed wait 9,270 cycles. Saturated cases report backpressure in all 12,000 measured cycles per seed. External pending requests are **not** counted as physical storage.

## Predictive necessary boundary: bank demand, not snapshot oracle

For a sustained, lossless offered stream with per-request long-run read demand `d_b` on bank `b`, bank port capacity `P_b`, output capacity `K`, and offered rate `lambda`, conservation gives the **necessary** throughput ceiling

```
T <= min(lambda, K, min_b(P_b / d_b))   for banks with d_b > 0.
```

This is a capacity upper bound, **not** a new scheduling theorem or sufficient positive speedup law. Finite-window transients and stochastic sample variation can perturb its empirical comparison.

- **Constructed four-bank workload:** bank 1 receives four reads per four offered requests, so `d_1=1` and `P_1=2`: `T<=2`. Greedy already achieves 2.0000, so a 3-vs-2 *snapshot* grant count cannot become sustained throughput. The same bound holds at K=2.
- **65%-hot workload:** bank 0 has expected `d_0=2(0.65)=1.3` reads/request; `T<=2/1.3=1.53846` requests/cycle in the long-run distribution. Measured greedy is `54,231/36,000=1.50642`, already within about 2.13% of the optimistic bank limit; the tested head-optimal policy yields no gain.
- **Uniform16:** output K=4 is the tight simple bound; greedy is `137,372/36,000=3.81589`, challenger `3.81625`. The ceiling alone does not predict the tiny residual advantage.
- **Low-load:** the offered-rate ceiling `lambda=1` is met by both.

A genuine positive law must additionally predict the *state-dependent* bank-collision and FIFO-head distributions from independent workload features, then survive unseen traces and physical implementation. No such law survives here.

## Independent audit
The independent checker **does not import the evaluator**. It recursively enumerates feasible subsets, replays the complete 15,000-cycle trace independently for both policies and all 15 seed/regime pairs, checks offered/admitted/completed/upstream/FIFO conservation and on-chip wait <=7, and exhaustively enumerates **65,536** four-bank operand tuples for K=2 and K=4. Exact four-bank aggregate grants: K=2 greedy/head **129,604/129,604**; K=4 greedy/head **171,076/173,572**. Independent full-trace audit: **PASS** locally.

The evaluator's deterministic pretty-printed JSON output has SHA-256 `31381136fe68d83c84a11a6c7fac5d111930c2492cefa757249943d19eadd3e5`. [Hosted reproduction #41486318359](https://github.com/sushxnthd/vektor/actions/runs/41486318359) **completed successfully** on source commit `1c7f8c41`; it regenerated the frozen SHA-256, independently replayed all traces, passed exhaustive four-bank checks, and archived both raw JSON files in [artifact #13162641410](https://github.com/sushxnthd/vektor/actions/runs/41486318359/artifacts/13162641410). This is hosted algorithmic reproduction, **not** RTL/EDA physical signoff.

## Architecture applicability and prior art
The 4-slot, 2R/bank model is a synthetic bank-port stress test, **not a verified Blackwell/RTX 5090 execution model**. The [GPGPU-Sim operand collector documentation](https://gpgpu-sim.org/manual/index.php/Main_Page) describes a banked collector/arbitration model, but [Huerta et al., MICRO 2025, DOI 10.1145/3725843.3756041](https://doi.org/10.1145/3725843.3756041) report substantially different compiler-guided dependency/issue and register-access behavior in studied modern NVIDIA GPUs. Therefore a positive result in this legacy-like model would still require SASS-level validation and workload-derived port demand before any modern-GPU claim.

## Decision
**Kill this finite-FIFO head-preserving oracle as a prospective throughput mechanism under the frozen regimes.** Preserve the failed structured positive prediction, the earlier hot-bank and V317 physical falsifications, and the independent checker. No second architecture mechanism is promoted. Same branch, draft PR #34, no merge. V317's competent compact-greedy area dominance and illegal RF-proxy electrical routes remain binding. No SRAM macro, legal integrated GPU tile, calibrated power, measured GPU IPC or RTX 5090 equivalence is demonstrated.
