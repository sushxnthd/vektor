# V296: clock-label placebo falsifies architecture-specific attribution (2026-10-25)

**Evidence tier:** preregistered unseen *synthetic* event streams, same exact wall-time bank/memory model, independent priority oracle and FIFO/bandwidth checks. Not physical GPU evidence. [Frozen protocol](CLOCK_LABEL_PLACEBO_PREREG_20261025.md) was committed as `2be310b9` before the new seeds were evaluated. Executable negative control: `python3 research/v296/clock_label_placebo.py --self-test` and `--evaluate`.

## Decisive negative-control finding

The existing `matched_walltime_workload.py` exposes only `replay(events, period, bandwidth, bucket)`. **It does not accept an architecture label and calls the same arbitration algorithm for both V296 and serial.** Thus any difference between the prior 3 ns candidate and 4 ns serial comparison is a consequence of the *assumed period*, not a demonstrated V296-specific improvement. For any fixed event stream and resources, `T(V296, p)=T(serial, p)` **by construction of this synthetic simulator**. This is not a proof of real RTL/tile performance equality after different physical implementations.

Preregistered independent synthetic seeds and results (units: issued waves/ns):

| Frozen regime | Seed | Bandwidth | T at 4 ns | T at 3 ns | Original candidate/serial ratio | Swapped-label ratio | Both equal-clock ratios |
|---|---:|---:|---:|---:|---:|---:|---:|
| clock_only_win | 296501 | 20 GB/s | 0.7294375 | 0.8644167 | 1.185046 | 0.843849 | 1.000000 |
| bandwidth_no_win | 296502 | 1 GB/s | 0.1250000 | 0.1250000 | 1.000000 | 1.000000 | 1.000000 |
| hotspot_stress | 296503 | 20 GB/s | 0.3455417 | 0.4272292 | 1.236404 | 0.808797 | 1.000000 |

All preregistered invariance and numeric win/no-win predictions passed. Clock swaps reciprocated the original apparent gains to 1e-12. Same-clock throughput ratios were exactly 1 for both 3 ns and 4 ns assignments. The high-hotspot case demonstrated that even a 23.64% assumed-period effect can be entirely independent of architecture identity.

The previously reported synthetic +18.20% case is still numerically correct as a **conditional faster-clock scenario**. It is *not* an observed V296 advantage, and these placebo controls make that distinction experimentally explicit.

## Falsification decision

**Architecture-specific workload speedup in this model: NOT IDENTIFIABLE; conditional clock-period-only gains: IDENTIFIED.** A future performance claim requires (1) both implementations passing matched postroute setup/hold/cap/slew/DRC gates, (2) measured or physically justified feasible periods, (3) independently optimized equal-resource serial comparator, and (4) architecture-distinct RTL/tile behavior under matched event streams and bandwidth. The original 3.5 ns gate remains BOTH_INFEASIBLE. No clock ratio, GPU power, or RTX-5090-equivalence claim follows.

The synthetic placebo did not open real GPU trace holdouts. V296 remains the only provisional mechanism under falsification; V287 stays retired. Kernellum PR #119 and all other workstreams remain untouched.

## Reproduction and caveat

The test script was executed locally against a faithful local copy of `matched_walltime_workload.py`, and its self-test printed `V296_CLOCK_LABEL_PLACEBO_SELFTEST_PASS`. Hosted CI execution of this new test is **not yet verified**. The checker's structural identity result depends on the fact that both architecture labels use exactly the same replay function; it does not compare distinct postroute implementations.
