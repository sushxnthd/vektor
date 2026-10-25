# V296: fixed-port maximum-admission oracle exposes a policy ceiling (2026-10-25)

**Evidence tier:** exact rational enumeration plus independent synthetic request simulation. **Not** a measured GPU workload, an implemented scheduler, a matched-area comparison, or physical closure. V296 remains the **sole active hardware mechanism**; V287 remains retired.

## Prospective protocol and implementation
The [protocol](OPTIMAL_SUBSET_ADMISSION_ORACLE_PREREG_20261025.md) was frozen at commit `e5b80ee396f6092d9f054a41609a286a6a527cdf`, before the two seeded synthetic evaluations. [Executable checker](optimal_subset_admission_oracle.py) was committed separately at `4a69d792440363e8d513efed5efbbda3999d02f6`; [frozen results](OPTIMAL_SUBSET_ADMISSION_ORACLE_RESULTS_20261025.json) were committed at `2ff9858f112e1d2bd2588235780e973a83555353`. The checker passed local exhaustive self-tests: an independent recursive maximum-subset oracle agreed with bitmask enumeration on every three-slot/two-bank request vector; bank-label permutation, operand swapping, and read-port capacity invariants passed. Hosted execution is **not yet verified**.

The **greedy** policy is the shared V296 and serial-one-hot admission semantics: process four requests in priority order, admit each if its two operand-bank reads fit within two ports per bank. The **oracle** enumerates all subsets and maximizes the number of admitted requests under the *same bank-port and issue-slot limits*. It is a mathematical comparator only: it can skip older requests and has not been implemented, synthesized, timed, area-matched, or proven fair.

## Frozen results

| Regime | Greedy admissions/cycle | Oracle admissions/cycle | Absolute oracle advantage | Relative oracle advantage |
|---|---:|---:|---:|---:|
| **Exact**, 3 banks, 4 slots, p=0.8, rho=0.2 | 1.938336 | 2.033758 | **0.095422** | **+4.923%** |
| **Predicted oracle-win**, 4 banks, p=0.95, rho=0.2, 120,000 seeded cycles | 2.453600 | 2.559583 | **0.105983** | **+4.320%** |
| **Predicted near-no-win**, 16 banks, p=0.20, rho=0.2, 120,000 seeded cycles | 0.788908 | 0.789017 | **0.000108** | **+0.0137%** |

The exact rational regret for the 3-bank case is **27172864/284765625** admissions/cycle. Probability mass sums to exactly one. The oracle outperformed greedy on **10.5983%** of high-contention cycles and **0.01083%** of low-contention cycles. Both preregistered signed magnitude gates passed. Conservative 99% two-sided Hoeffding intervals for the paired regret are **[0.087189, 0.124778]** and **[0, 0.018903]**, respectively. The low-contention *point estimate* passes the frozen near-no-win threshold; its conservative 99% interval is too wide to establish a population regret below 0.01. Do not interpret that gate as a statistically demonstrated strict upper bound.

### Compact strict-positivity law (limited workload family)
For independent request validity `p`, uniform first bank over `B` banks, and second operand equal to the first with probability `rho` (otherwise independently uniform), define the per-request probabilities

```
u = p (1-rho)/B^2                        # specified ordered distinct-bank pair
v = p [rho/B + (1-rho)/B^2]            # specified same-bank pair
```

For `B>=3`, the disjoint four-request motif `(a,b), (a,a), (b,b), (c,c)` with distinct `a,b,c` has probability

```
P_motif = B(B-1)(B-2) * u * v^3 .
```

On every such motif, greedy admits requests 0 and 3 (two), while the maximum subset admits requests 1, 2 and 3 (three). Since the oracle never admits fewer than greedy,

```
E[oracle admissions - greedy admissions] >= P_motif > 0
```

whenever `B>=3`, `p>0`, and `0<=rho<1`. This is a **strict, conservative lower bound**, not an exact general regret law. It is **0.0009774075** for the frozen four-bank high-contention distribution, versus observed regret 0.105983. It proves that the shared priority-greedy policy can leave capacity unused; it does **not** establish any V296-specific throughput gain.

## Architecture decision and physical implications

**The equal-clock V296-versus-serial throughput advantage remains exactly zero**, because both execute the *same* priority-greedy selection on the same requests. The oracle's +4.32% synthetic admission opportunity is **not attributable to V296** and must not be reported as a GPU speedup. The oracle is not the strongest *equal-cell-area* alternative until an independently optimized, fair implementation survives RTL equivalence, synthesis, detailed route, electrical/hold/setup closure and matched power/area. The current strongest physically tested control remains serial one-hot, with other parallel one-hot comparisons preserved.

The original integrated 3.5 ns gate remains **BOTH_INFEASIBLE**: V296 setup -1.047895 ns and hold -0.036622 ns, serial setup -1.859922 ns and hold -0.019796 ns, with three capacitance violations each. The independently recovered critical setup path runs from scheduler round-robin state to executed-data flops. These results reinforce the next priority: **matched scheduler-to-executed-data logic-topology repair**, separately optimized for candidate and strongest serial control, with extracted RC, setup/hold/cap/DRC and equal-consumed-area checks. Do not switch the active mechanism to the unimplemented oracle. Keep prospective GPU holdouts sealed.

**World-class completion gate: NOT REACHED.** No physically feasible integrated GPU throughput improvement, silicon power measurement, real-workload prediction, or RTX-5090-equivalence claim is supported.
