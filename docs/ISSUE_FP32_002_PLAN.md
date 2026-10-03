# FP32-FMA-002 — bounded-width production-lane discrimination

**Class:** DISCRIMINATION + CAPABILITY-BUILDING  
**Status:** preregistered; implementation gate open  
**Parent evidence:** FP32-FMA-001 exact 556-bit simulation oracle

## Question

Can a synthesis-oriented fused binary32 lane preserve the bit-exact result behavior of the FP32-FMA-001 oracle without carrying the oracle's 556-bit global lattice into hardware?

This experiment deliberately separates **correctness reference** from **production microarchitecture**. The exact reference remains simulation-only evidence. No throughput, clock, area, or 5090-class claim follows from this plan.

## Competing mechanisms

### H1 — bounded fused significand is sufficient
Use normal IEEE-754 decomposition, a 24x24 -> 48-bit product, exponent comparison/alignment, bounded carry/guard/round/sticky state, signed add/subtract, leading-zero normalization, and one final RNE rounding. Pipeline boundaries are inserted only after state needed for exact final rounding is preserved.

Prediction: bit-for-bit results match the exact oracle across the frozen 10k+ corpus and new cancellation-focused vectors, while generic synthesis completes inside the existing 180 s budget.

### H2 — naive sticky compression fails under cancellation
A conventional G/R/S compression performed *before* a subtractive near-cancellation can destroy information later promoted by normalization.

Prediction: an intentionally naive bounded implementation will show mismatches concentrated around opposite-sign, close-exponent cases. This negative control is required before accepting any optimized compression rule.

### H3 — special-case/control logic, not significand width, dominates synthesis
The 556-bit lattice may not be the only cause of the prior timeout.

Prediction: after replacing the lattice with bounded datapath widths, synthesis may still show pathological mux/priority logic. If so, the next experiment isolates leading-zero detection, variable alignment, and special-case selection separately.

## Preregistered gates

A candidate production lane is **not validated** unless all gates pass on one exact commit:

1. **Result equivalence:** zero mismatches against the frozen >=10,000 glibc-fmaf result corpus.
2. **Directed IEEE cases:** NaN/invalid, infinity, overflow, exact/subnormal underflow, cancellation, and signed-zero cases remain green.
3. **Cancellation stress:** add deterministic generated cases where product and addend have opposite signs and exponents within 0..30, including exact and near cancellation. Minimum 10,000 additional cases.
4. **Boundary stress:** deterministic cases around normal/subnormal and overflow boundaries and halfway RNE decisions.
5. **Synthesis completion:** Yosys generic synthesis finishes in <=180 s on GitHub Actions.
6. **Evidence separation:** synthesis cell counts are reported as synthesized generic logic only; frequency/area/power remain UNTESTED until a technology-mapped flow exists.

If any equivalence mismatch occurs, record the first counterexample and cluster mismatches by exponent delta, sign relation, normalization shift, and result class before changing the design.

## Planned production stages

| Stage | Function | State that must survive |
|---|---|---|
| S0 | classify/unpack | sign, class, unbiased exponent, 24-bit significand |
| S1 | multiply/prepare C | 48-bit exact product, C significand/exponent, special-case metadata |
| S2 | compare/align | common exponent, bounded aligned magnitudes, discarded-tail summary that is cancellation-safe |
| S3 | signed accumulate | exact-enough magnitude/sign for final rounding |
| S4 | normalize | leading-zero shift, exponent correction, rounding tail |
| S5 | RNE/pack | binary32 result + {NV,DZ,OF,UF,NX} |

The lane may change latency. Throughput target is one accepted operation/cycle after fill, but this is a target until RTL and synthesis demonstrate it.

## Anomaly-mining fields

Every mismatch/synthesis result must log:
- sign(product) vs sign(C)
- product exponent minus C exponent
- leading-zero count after accumulation
- normal/subnormal/overflow result class
- exact/halfway/inexact rounding class when known
- synthesis runtime
- cell counts by arithmetic/mux/compare/shift family

Regime boundaries, not aggregate pass rate, decide the next design.

## World-model update

- **KNOWN:** the 556-bit exact-lattice reference has passed the frozen result corpus and directed flag checks in simulation.
- **KNOWN:** generic synthesis of that reference exceeded the 180 s budget in FP32-FMA-001.
- **FALSIFIED:** treating the 556-bit correctness oracle itself as an acceptable production-lane implementation under the current synthesis budget.
- **BELIEVED:** bounded exponent-relative alignment can remove the pathological global lattice while retaining fused single-rounding semantics.
- **UNTESTED:** exact bounded width/compression rule; pipeline frequency; technology-mapped area/power; 128-lane tile feasibility.
- **ANOMALOUS:** none yet for FP32-FMA-002; first counterexamples are explicitly evidence, not bugs to hide.

## Cheapest next decisive action

Implement H2 first as a negative control and H1 as the candidate behind the same differential testbench. Generate cancellation-focused vectors from the host fused oracle, run both against identical seeds, and synthesize H1 only after zero mismatches. This directly tests whether early sticky compression is the dangerous mechanism while avoiding another expensive 556-bit synthesis attempt.
