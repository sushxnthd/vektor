# V309: four-read-counter collision impossibility (2026-10-30)

**Result:** HOSTED PASS, [GitHub Actions #41034856696](https://github.com/sushxnthd/vektor/actions/runs/41034856696), artifact `v309-read-counter-collision` (ID 12967601561). **Evidence tier:** retrospective published, unmatched profiler-counter sample. No hardware candidate promoted.

## What was tested
[Protocol frozen before implementation](READ_COUNTER_COLLISION_PROTOCOL_20261030.md) at commit `d6006492c561e4e4cc5bf77ad59d100ef3aacb85`; [executable independent audit](read_counter_collision.py) and a separate O(n²) pairwise oracle. The published source was inspected before protocol formation, so **this is not prospective or unseen**.

Input is the same source-pinned 25-row Accel-Sim GV100 sample, [upstream commit 7ba54ded](https://github.com/accel-sim/accel-sim-framework/blob/7ba54ded60c4ba0083410c37d22d719166acd6dc/util/accelwattch/accelwattch_hw_profiler/hw_perf.csv), Git blob `aa88bb2566ff3b3e012442cd20bc753127732cac`. Existing strict parser checks source identity, duplicate keys and finite nonnegative Decimal values.

The proposed input feature sets were (a) `L1_RM,L2_RM` and (b) the stronger `L1_RH,L1_RM,L2_RH,L2_RM`. No target-dependent, kernel-identity or write-counter features were used.

## Verified exact collisions

| Property | Two read-miss counters | All four read counters |
|---|---:|---:|
| Rows | 25 | 25 |
| Distinct feature vectors | 22 | 22 |
| Feature vectors with different positive DRAM_Rd targets | 2 | 2 |
| Strongest collision feature vector | (0,0) | (0,0,0,0) |
| Strongest collision rows | 3 | 3 |
| Smallest DRAM_Rd in strongest collision | 5.952380952380952 | 5.952380952380952 |
| Largest DRAM_Rd in strongest collision | 640 | 640 |
| Target ratio | **107.52×** (approximately) | **107.52×** (approximately) |
| Unavoidable worst-case multiplicative error | **at least 10.369×** | **at least 10.369×** |

The three exact read-counter-zero rows are `binomialOptions :: _Z21binomialOptionsKernelv`, `quasirandomGenerator :: _Z26quasirandomGeneratorKernelPfjj`, and `quasirandomGenerator :: _Z16inverseCNDKernelPfPjj`. Their published `DRAM_Rd` values are 640, 21 and 5.952380952380952, respectively. The other collision is `fastWalshTransform` versus `mergeSort` at four-counter feature vector `(0,1048576,0,1048576)`, with DRAM_Rd 1,048,581 versus 1,048,580.

### Sharp lower-bound law
For two rows with exactly the same feature vector and positive targets `0<y_min<y_max`, every deterministic estimator must output the same positive prediction `p` on both. Therefore

`max(p/y_min, y_max/p) >= sqrt(y_max/y_min)`.

The **strongest possible oracle groupwise constant** `p=sqrt(y_min*y_max)` attains this minimax bound. Here `sqrt(640/5.952380952380952) ~= 10.36918511745`. The corresponding sharp additive minimax error is `(640-5.952380952380952)/2 ~= 317.02380952381` counter units. The implementation compares the exact Decimal squared multiplicative bound against an independent O(n²) pairwise oracle; no floating tolerance decides collision identity.

## Falsification and scope
**KILL:** every claim that a deterministic function of only the four published read-hit/miss counters can *exactly reconstruct all 25* published DRAM-read values, regardless of nonlinear model complexity. This is stronger than the preceding zero-intercept linear falsification.

**DO NOT CLAIM:** that all counter-based DRAM models fail, that write/bypass features cannot help, that the CSV records per-instruction events, or that a 10.37× error is an observed hardware prediction error. The bound is for an explicitly restricted input space and published counter targets. The CSV collection conventions and hardware provenance remain unverified. It is not matched to the historical V309 Rodinia 2.0-ft SASS archive.

## Hardware decision
No architecture mechanism is promoted or revived. This is a **counter-observability negative result**, not physical design evidence. Do not infer DRAM traffic, bandwidth-limited speedup, RTL area, power, timing or RTX 5090 equivalence from it. Preserve previous V309 trace reconstruction and cache-line falsifications.

**Next decisive gate:** stop expanding unmatched counter proxies. Acquire one matched source-authenticated trace + same-run profiler counters (cache lines/sectors, DRAM reads/writes, stalls, occupancy) + validated cycle-model calibration. Then preregister one positive and one no-win workload and test a single equal-resource hardware mechanism through RTL, synthesis, timing and wire/load sensitivity. If unavailable, report the blocker rather than invent a hardware advantage.

Kernellum PR #119 remains separate and unmodified.
