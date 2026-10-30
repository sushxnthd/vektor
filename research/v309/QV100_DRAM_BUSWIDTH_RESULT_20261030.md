# V309 QV100 DRAM bus-width counterfactual: prospective negative result (2026-10-30)

## Verification
**PASS, simulator-only sensitivity; no architectural win.** Frozen [protocol](QV100_DRAM_BUSWIDTH_PROTOCOL_20261030.md) committed at [94d79f0](https://github.com/sushxnthd/vektor/commit/94d79f0e29a4199114d81bbcdcb655243cef5063) before executable [ee544c8](https://github.com/sushxnthd/vektor/commit/ee544c8a1ec8f4495089c7e01e1ee06200f3e1a9) and hosted [workflow commit 243c415](https://github.com/sushxnthd/vektor/commit/243c415505f7fe0f83c8eddfaedc5b2a14612e55). [GitHub Actions #41106976532](https://github.com/sushxnthd/vektor/actions/runs/41106976532) **PASSED** on 2026-10-30 at 18:31 UTC. [Raw artifact #13002390491](https://github.com/sushxnthd/vektor/actions/runs/41106976532/artifacts/13002390491) contains 39 files, including all six new variant logs, SHA-pinned configs, manifest and independent audit, plus previous latency experiment. Artifact ZIP SHA-256: `fbcacfa7209b6ee2c300eecfc4be1746357d6f6c25c462a6edb41d5c146a65b0`.

The original source-pinned QV100-SASS simulator ran the authenticated Rodinia 2.0-ft Pathfinder `1000_20_5` command list, four kernel launches and two original HtoD copies. Exactly one active `gpgpusim.config` parameter was changed from `-gpgpu_dram_buswidth 16` to 8 or 32. All other options, including DRAM latency 100, were held byte-identical. Two full simulations per configuration passed the explicit completion marker and independent per-kernel semantic replay audit. Bus-width selftests passed 5 positive and 9 negative controls.

## Frozen outcomes

| Simulated bus width (bytes) | Total simulated cycles | Delta vs baseline | L1D misses | L2 misses |
|---:|---:|---:|---:|---:|
| 8 | 28,729 | +12 (+0.041787%) | 3,534 | 129 |
| 16 (unaltered) | 28,717 | 0 | 3,534 | 129 |
| 32 | 28,717 | 0 (0.000000%) | 3,534 | 129 |

All settings execute **1,059,640 simulated instructions** over the same four launches. The independent checker found **unchanged L1D and L2 miss counters** in both counterfactuals. All three preregistered directional tests survived: 8 is slower; 32 is not slower; the benefit of 32 is below 2%. Critically, the widening benefit is **exactly zero simulated cycles** for this workload. This is a prospective **negative result for bus-width expansion**, not evidence that the widened bus is physically free or beneficial.

## Scientific decision
**Kill any proposal to widen the DRAM bus as a Pathfinder throughput optimization on this evidence.** The observed response to halving width is only 12 cycles; doubling width has no benefit. Do not extrapolate this result to other workloads, to a true V100 bus-width change, or to energy/area. The bus-width option changes modeled hardware resources and therefore cannot be interpreted as an equal-resource architecture comparison. Cache counters are simulator counters, not independently measured hardware events.

This result complements the previous independent latency sweep: raising modeled DRAM latency 100 -> 400 increased cycles only 2.086%. Neither parameter sweep identifies the true dominant resource. **No V309 hardware mechanism is promoted**; V287/V296 remain retired. The next useful discriminating experiment is a *second, prospectively frozen workload* and then a single implementable matched-resource issue/occupancy/port candidate. Any surviving candidate must pass RTL, synthesis, electrical, matched timing/area, wire/load sensitivity and a prospective boundary-law holdout before an integrated GPU claim. Kernellum PR #119 and its holdouts are unchanged.
