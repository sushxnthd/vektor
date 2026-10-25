# V296 cross-slot bank dependence: exact falsification of the i.i.d workload boundary (2026-10-25)

**Evidence tier:** exact-rational stochastic admission model, with independently exhaustive small-case oracle; **not measured GPU traces, tile throughput, power, or physical closure**. [Prospective protocol](LATENT_HOTBANK_CORRELATION_PREREG_20261025.md) was committed first as `2ac00cbe`, before executing the new exact DP. Executable [checker](latent_hotbank_correlation.py) was committed as `8679207c`. V296 is the sole active mechanism; V287 remains retired.

## What was falsified

The previously established five-parameter `q(B,S,P,p,rho)` law is exact **only for the declared independent-request family**. It cannot predict all workloads with the same single-request validity, bank distribution and operand-overlap probability. A single latent cycle-level hotspot parameter `lambda` provides a constructive counterexample while preserving *every one-request marginal exactly*.

Draw a fresh uniformly distributed hotspot H once per cycle. For each issue slot, choose first operand bank A=H with probability lambda, otherwise uniformly from B; choose second operand C=A with probability rho, otherwise uniformly; independently mark valid with probability p. Therefore for every lambda, `Pr(A=k)=1/B` and `Pr(C=A)=rho+(1-rho)/B`. Only **joint dependence across slots** changes. Greedy admission remains identical for V296 and serial one-hot, and each request consumes two bank read ports.

## Prospective exact result

Frozen resource point: **B=16 banks, S=4 ordered issue slots, P=2 ports/bank, p=0.8, rho=0.2**. The exact-rational dynamic program conditions on H by symmetry and tracks its occupied ports separately from the histogram of all other banks.

| Latent hotspot lambda | Expected admitted waves/cycle, exact model | Change from i.i.d. |
|---:|---:|---:|
| 0 | 2.992340240625 | 0% |
| 0.25 | 2.901699409094 | -3.03% |
| 0.5 | 2.639247053320 | -11.80% |
| 1 | 1.675200000000 | **-44.02%** |

All preregistered predictions passed: strict ordering at the frozen point, `q(0)-q(1)>1`, `2.5<q(0.5)<2.8`, and exact recovery of the original i.i.d fraction `957548877/320000000` at lambda=0.

**Independent falsification:** a separate full enumeration of latent hotspots, valid flags, ordered operand pairs and a per-bank read-port oracle exactly matched the histogram DP for `(B,S,P,p,rho,lambda)=(2,3,2,0.75,0.3,0.65)`, `(3,2,2,0.5,0.25,0.4)` and an additional extreme case `(2,2,1,1,0,1)`. Exact fraction equality, probability conservation and invalid-input rejection passed locally. This does **not** constitute independent GPU workload validation.

## Corrected predictive law and bottleneck boundary

Replace the insufficient i.i.d scalar by `q(B,S,P,p,rho,lambda)`, evaluated exactly by the finite-state histogram recursion under the declared latent-hotspot family. A conditional tile-level throughput boundary is

```
R_j = min( q(B,S,P,p,rho,lambda) / [T_j (1+h_j)], W/b )
W_critical,j = b*q(B,S,P,p,rho,lambda) / [T_j (1+h_j)]
```

where T is **feasible integrated tile period**, h additional issue overhead, W sustained bandwidth and b bytes/useful wave. This law includes bank compatibility, read-port pressure, offered occupancy, intra-request bank overlap, cross-slot dependence, bandwidth and control overhead. It does **not** identify a V296-specific performance improvement: at equal clocks, overhead and resources, V296 and serial have the same q and same R by construction.

As a **post-analysis algebraic illustration, not a frozen GPU workload**, at T=3.5 ns, b=4 B/wave and W=2.5 GB/s, lambda=0 gives W_critical=3.419817 GB/s and is bandwidth-bound at 0.625 waves/ns, whereas lambda=1 gives W_critical=1.914514 GB/s and is bank/issue-bound at 0.478629 waves/ns. **The bottleneck classification reverses despite identical single-request statistics.** The periods and bandwidth here are assumptions, not measured tile values.

## Scientific decision and next test

**Result:** the independence assumption is materially consequential; the five-parameter law is falsified as a general workload predictor. The extended law is exact for its declared synthetic family and independently checked on small cases, but lambda is not inferred from real bank traces and no unseen real GPU workloads have been validated. More realistic correlations, temporal persistence, instruction dependencies, register mapping and scheduler feedback remain unmodeled. Do not assert that lambda is a universal sufficient statistic.

V296's original integrated post-route implementation and serial one-hot both remain infeasible at the frozen 3.5 ns electrical/timing gate. Separate controller-only post-CTS feasibility does not resolve integrated closure. The corrected extracted critical-path experiment [#40203738175](https://github.com/sushxnthd/vektor/actions/runs/40203738175) is the immediate physical priority; at the time of this report its candidate job had completed but its serial job was still running. Extracted endpoints and equal-consumed-area physical repair remain unverified. No GPU speedup, measured power, or RTX-5090 equivalence is claimed.

Next scientific experiment: freeze a prospective real bank-trace set, estimate lambda or a stronger dependence diagnostic from training-only traces, predict unseen q and W_critical, and compare with a strong empirical pair-collision baseline. Independently close both integrated physical designs and optimize the equal-area serial control before any architecture-performance claim. Kernellum PR #119 and existing holdouts remain untouched.
