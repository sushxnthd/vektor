# V296 fixed-word deep-bank transfer: analytical falsification and prospective synthetic checks (2026-10-27)

**Evidence tier:** deterministic analytical proof plus independent weighted-pair enumeration and seeded synthetic Monte Carlo. **Not** RTL deep-bank simulation, synthesis, routed timing, GPU workload, SRAM, energy, or silicon.

## Preregistration and provenance
Frozen protocol was committed first at `f8f904d4`, before evaluating the three prospective seeds. The independent Python checker was subsequently committed at `798fb18b`. A local implementation of the same algorithm passed its self-tests, exact weighted enumeration, exhaustive address-coverage checks and all 24 seeded Monte Carlo acceptance cells. The exact committed file has **not yet received hosted CI validation**. The pre-existing real workload holdouts remain sealed.

## Decisive functional counterexample
The currently routed V296 fixed-word RF proxy exposes two static word outputs per bank. For any bank with D>2 independently addressable words, choose an unexposed word index 2 and distinct stored values (13,26,39, ...). A valid two-read request (2,2) must return (39,39); no selection/broadcast of static outputs 0 and 1 can produce 39. This is a deterministic **functional inequivalence** for the proposed static readout extension. It holds irrespective of clock period, synthesis, or traffic skew.

The existing fixed-word `v296_tile_slice_fixed_word.sv` also derives each operand word from `wave_id[0]`, which cannot represent arbitrary deeper-bank addresses. Therefore the two-word implementation must not be extrapolated to production-depth register files.

## Positive statistical eligibility boundary (not throughput)
For word probabilities p and within-pair address copy probability rho, define m as the probability mass of the two most frequent word addresses. The **maximum** probability that two static outputs cover both reads is

`P_covered = rho*m + (1-rho)*m^2`.

The formula is exact for the frozen request generator; choosing the top two p entries is optimal. A dynamic two-address/two-read-port reference covers every valid pair functionally, but needs dynamic selection and its physical cost is unmeasured.

| Frozen regime | Depth | rho | Best two-word mass | Predicted coverage | Three independently sampled coverages (100k each) |
|---|---:|---:|---:|---:|---|
| Uniform | 2 | 0.2 | 1.0000 | 1.000000 | 1.00000 / 1.00000 / 1.00000 |
| Uniform | 4 | 0.2 | 0.5000 | 0.300000 | 0.30051 / 0.30214 / 0.30232 |
| Uniform | 8 | 0.2 | 0.2500 | 0.100000 | 0.09925 / 0.09947 / 0.10077 |
| Uniform | 16 | 0.2 | 0.1250 | 0.037500 | 0.03677 / 0.03736 / 0.03833 |
| Uniform | 32 | 0.2 | 0.0625 | 0.015625 | 0.01524 / 0.01531 / 0.01584 |
| Skewed 0.55/0.25 | 16 | 0.2 | 0.8000 | 0.672000 | 0.67402 / 0.67044 / 0.67364 |
| Skewed 0.90/0.05 | 16 | 0.8 | 0.9500 | 0.940500 | 0.94198 / 0.93963 / 0.93993 |
| Skewed 0.50/0.25 | 16 | 0.8 | 0.7500 | 0.712500 | 0.71769 / 0.70980 / 0.71258 |

All 24 seeded trials passed the frozen absolute-error gate of 0.012; maximum observed absolute error **0.00519**. Independent weighted enumeration matched all eight predictions within 1e-12; exhaustive optimal static-choice enumeration matched the selected top-two pair. Exact ordered-pair coverage for a uniform D-word bank is 4/D² at rho=0; any D>2 has uncovered pairs. The intentionally false `coverage=1 for D>2` baseline is rejected.

**Important limitation:** This is a transfer *falsification*, not evidence that V296 arbitration itself is useless. P_covered measures static-readout address eligibility, not delivered throughput or energy; high coverage still does not establish correctness for arbitrary programs.

## Research decision and next hard experiment
**Kill fixed-word static readout as a general deep-bank V296 implementation.** Preserve its successful 2-word routed physical result as a narrowly scoped proxy. Keep V296 pairwise bank admission the sole provisional architecture mechanism and V287 retired. Do not reuse the 2-word area/timing figures to infer deep-bank advantage.

The next physically meaningful implementation must use an addressable, equal-capacity **dynamic two-port deep-bank RF** for *both* V296 and strongest serial control, with matched bank count, word depth, width, port count, pipeline and memory technology. First establish RTL cycle equivalence and independently feasible routed setup/hold/cap/slew/DRC for both. Then evaluate area, realistic wire/load, bandwidth, occupancy, measured-clock workload rates and prospective unseen workloads. A deep-bank transfer failure must be reported, not rescued by switching back to the 2-word proxy. No RTX-5090 equivalence claim.

Kernellum PR #119, prospective holdouts and other workstream branches were not modified.
