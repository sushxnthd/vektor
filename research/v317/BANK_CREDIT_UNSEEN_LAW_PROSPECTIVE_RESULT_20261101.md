# V317: prospective unseen bank-credit synthesis law, source-pinned result (2026-11-01)

## Frozen prediction and executed evidence
The seven predictions were frozen in [FROZEN_BANK_CREDIT_UNSEEN_SB_LAW_20261101.md](FROZEN_BANK_CREDIT_UNSEEN_SB_LAW_20261101.md) **before** synthesis, and the frozen list was not revised. [GitHub Actions #41288521132](https://github.com/sushxnthd/vektor/actions/runs/41288521132) at commit `e6ac67455b31df967d0f5cee838f4d862845b615` **completed successfully** at 2026-11-01 09:27:28 UTC. It executed seven independently checked RTL oracle configurations, seven matched bank-mask and pairwise generic syntheses, and a frozen prediction scorer. The [complete artifact #13076372441](https://github.com/sushxnthd/vektor/actions/runs/41288521132/artifacts/13076372441) preserves the full logs, netlists, source SHA, and machine-readable scoring. These are *unseen parameter configurations*, not independent GPU workload samples.

The prediction is `C(S,W) = 14*S*S - 17*S + 2 + (4*S*S - 2*S - 2)*(W-2)`, with `W=log2(B)`. This is a generic Yosys cell-count law for one RTL implementation and toolchain, **not** a predictive GPU throughput or silicon-area law.

| Slots S | Banks B | Frozen prediction | Observed pairwise cells | Matched bank-mask cells | Pairwise generic depth | Scored |
|---:|---:|---:|---:|---:|---:|---|
| 2 | 8 | 34 | 34 | 135 | 8 | PASS (exact) |
| 4 | 32 | 320 | 320 | 2,645 | 17 | PASS (exact) |
| 8 | 8 | 1,000 | 1,000 | 1,812 | 32 | PASS (exact) |
| 3 | 8 | 105 | 105 | 414 | 12 | PASS (within 10%; exact) |
| 5 | 32 | 531 | 531 | 3,718 | 21 | PASS (within 10%; exact) |
| 6 | 32 | 794 | 794 | 4,795 | 25 | PASS (within 10%; exact) |
| 7 | 8 | 749 | 749 | 1,535 | 28 | PASS (within 10%; exact) |

**Prospective outcome:** 7/7 frozen predictions passed; observed relative error was exactly zero in all seven. The last four hold out slot counts, not just bank-index widths. The entire grid remains a single Yosys/RTL implementation family, so exact prediction is consistent with a stable syntactic synthesis template and is not evidence of a universal silicon cost law.

## Falsification and baseline accounting
The matched bank-mask implementation uses the same S, B, two reads per admitted request, and the same fixed-priority grant semantics. Independent RTL oracle checks passed in the hosted workflow. This is *not* an equal-physical-area, equal-frequency or equal-energy comparison. The prior S=4,B=16 fixed-priority source and new parameterized bank-mask source also differ in generic synthesis cost, so never silently mix them.

**Throughput null:** The pairwise and bank-mask implementations grant exactly the same requests by construction under the proved algorithmic invariant. At fixed clock, register-file port capacity and queue behavior, their intrinsic completed-service ratio is exactly **1.000x**. A hardware implementation cost saving is useful for budget or timing, but cannot be presented as a scheduling throughput speedup.

The law is *not* the required positive boundary law in compatibility, mask overlap, bandwidth, occupancy and control overhead for a surviving GPU architecture mechanism. Do not upgrade it into such a claim.

## Remaining gates and decision
1. Prove the *parameterized RTL* equivalent over complete inputs at selected unseen S/B points, not merely sampled random test vectors.
2. Perform matched standard-cell mapping with a pinned liberty and constraints, then actual load/fanout, setup/hold and routed RC checks. Generic depth is not delay.
3. Compare against equally optimized fixed, rotating, and oldest-first fairness-aware controls. Collect dynamic bank traces and tile-level area/power before any system-level claim.
4. If no positive service advantage survives the strongest equally informed control and physical budget, retain pairwise bank-credit only as a low-cost implementation baseline, not an active novel architecture mechanism.

**Decision:** The prospective *generic-cell implementation-cost* law survives all seven holdouts. A GPU throughput breakthrough is **not** established. No RTX 5090 equivalence, silicon area, routed timing, dynamic power or real workload IPC is claimed. Kernellum PR #119 remains separate and untouched.
