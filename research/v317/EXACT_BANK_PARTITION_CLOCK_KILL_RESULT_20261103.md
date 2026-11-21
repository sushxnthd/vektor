# V317 exact bank-opportunity boundary and clock-kill envelope (2026-11-03)

**Evidence:** exact combinatorial proof-by-exhaustive-partition-enumeration plus seeded synthetic holdouts; NOT measured GPU IPC, physical bank mapping, RTL, SRAM signoff, or an implementable scheduler. Existing V317 physical/electrical failures remain binding. The existing V317 branch/PR remains the only primary workstream.

## Frozen protocol and independent transfer
[Frozen initial bank-scaling protocol](FROZEN_BANK_SCALING_CLOCK_ENVELOPE_20261103.md) was committed at `a9978f0` before the new B=8/16/24/32 draws. [Frozen exact-law transfer](FROZEN_EXACT_BANK_PARTITION_LAW_TRANSFER_20261103.md) was committed at `7315cf8` before evaluating B=12/48/64 seeds 4111, 5113, 6113 (12,000 vectors per seed per B). Independent audit separately enumerated all 3^8=6,561 and 4^8=65,536 assignments and replayed all 108,000 new holdout vectors, without importing the evaluator.

## Exact predictive law, within the restricted model
Four initially valid ordered requests, each with two independently and uniformly mapped bank operands; two reads/bank/cycle; issue cap two; two cycles; oldest-pending request must issue each cycle. The oracle has full four-request lookahead and is an **upper bound**, not a feasible hardware controller. Let `(B)_k` be the falling factorial and `E` the event that oracle finishes one more request than greedy. Enumeration of all 4,140 partitions of eight operand positions gives:

```
Pr(E | B) = [153(B)_3 + 212(B)_4 + 61(B)_5 + 4(B)_6] / B^8
E[G | B] = [2(B)_1 + 404(B)_2 + 3511(B)_3 + 6536(B)_4
            + 4139(B)_5 + 1060(B)_6 + 112(B)_7 + 4(B)_8] / B^8
R_oracle(B) = 1 + Pr(E | B) / E[G | B]
```

For large B, `Pr(E|B) = 4/B² + O(B⁻³)` and `R_oracle(B) = 1 + 1/B² + O(B⁻³)`. The mechanism is rare bank collisions that both harm the greedy residual pair and admit an alternative first-cycle pairing. This exact law assumes iid-uniform mapping, no register-cache hits, no physical wiring, no arrivals, no queuing, and full oracle lookahead. It is **not** a positive GPU architecture mechanism.

## Prospective unseen-bank holdouts
| B | Exact Pr(E) | Observed opportunities / 36,000 | Exact oracle gain | Observed ratio at 0.5% extra period |
|---:|---:|---:|---:|---:|
| 12 | 2.59990% | 1,001 (expected 935.96) | +0.65459% | 1.001993× |
| 48 | 0.17347% | 62 (expected 62.45) | +0.04339% | 0.995453× |
| 64 | 0.09770% | 39 (expected 35.17) | +0.02443% | 0.995294× |

All frozen five-sigma transfer checks passed. B12 predicted-win and B48/B64 predicted-no-win under the **illustrative conditional** 0.5% added period also passed. A shared bandwidth cap of 95% of greedy's compute capacity eliminates the benefit in the fluid ceiling. These are conditional algebraic rate comparisons for repeated independent batches, not GPU throughput results.

Initial seeded bank-scaling sensitivity (3 seeds × 8,000 vectors per B):
| B | Greedy completions | Oracle completions | Oracle ceiling gain | Max added delay at illustrative 2 ns |
|---:|---:|---:|---:|---:|
| 8 | 94,493 | 95,779 | +1.36095% | 27.219 ps |
| 16 | 95,626 | 95,985 | +0.37542% | 7.508 ps |
| 24 | 95,844 | 95,992 | +0.15442% | 3.088 ps |
| 32 | 95,916 | 96,000 | +0.08758% | 1.752 ps |

A simple `k/B²` fit to B8 and B16 predicted B24/B32 event rates within 2.18% and 1.27% relative error; the exact combinatorial law supersedes that empirical fit. In the synthetic batch model the necessary clock boundary is `delta_period / period < R_oracle(B)-1`; the actual controller must do **better** than this impossible-oracle threshold to claim a gain.

## Architecture decision
**Do not promote a new scheduler.** At 16–64 banks even the clairvoyant synthetic ceiling is very small and a 0.5% clock penalty erases it at B16 and above. The prior 734-vs-260 generic-cell degree-controller comparison is not routed area and is not an area-matched implementation of the oracle. Demand provenance-pinned compiled workloads, dynamic bank demand, cache/reuse assumptions, a strong compact equal-resource controller, electrical timing, area/power and tile-level traffic before revisiting physical implementation. No RTX 5090 equivalence claim.

Reproduce: `python -m research.v317.rtl.exact_bank_opportunity_polynomial`; `python -m research.v317.rtl.exact_bank_partition_transfer > /tmp/transfer.json`; `python research/v317/rtl/audit_exact_bank_partition_transfer.py /tmp/transfer.json`.

## Hosted independent reproduction
[GitHub Actions #41558336838](https://github.com/sushxnthd/vektor/actions/runs/41558336838) **completed successfully** on the latest research commit. It re-derived the exact partition coefficients, reran the frozen 108,000-vector unseen transfer and 96,000-vector bank-scaling replay, independently audited both, and uploaded [raw JSON evidence artifact #13196245152](https://github.com/sushxnthd/vektor/actions/runs/41558336838/artifacts/13196245152). This verifies reproducibility of the synthetic boundary, not electrical legality or GPU performance.
