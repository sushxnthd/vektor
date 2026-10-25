# V296 matched integrated RF-slice: BOTH contestants fail the frozen physical gate (2026-10-25)

**Decision: FALSIFIED under the original integrated-slice constraints.** This is the completed *paired* follow-up to the earlier candidate-only failure. It does not overturn the controller-only positive timing result, but that result is not a tile-level GPU speedup.

## Provenance and scope

Original unmodified paired OpenROAD run [40156470550](https://github.com/sushxnthd/vektor/actions/runs/40156470550); completed candidate job `121059038926`, completed serial-onehot job `121059038944`, independent aggregate job `121075643212`. The aggregate exited with code 3 **by design**, returning `CANDIDATE_TILE_SLICE_PHYSICAL_GATE_FAIL` after independently auditing both completed artifacts. Original artifacts: pairwise `12585654946` (ZIP SHA256 `06bfdd796801728553fa6c42e853957fb681e52731c73641a9aed403f2905544`), serial `12586607915` (ZIP SHA256 `5456c370dc860daa67aa61c7a8dc9937291f2b5d89e4e8e51c4ebedf14c6fd1d`), aggregate `12585833656` (ZIP SHA256 `74d049ffa025172fc57d91242d38707f39291e02947f9d4c70f831e036f8edad`). Source: the original aggregate job's printed `aggregate.tile_slice.json`, not a rerun with modified constraints.

Evidence tier: post-CTS propagated-clock, detailed-route OpenRCX, 2x extracted RC, Nangate45. **Not signoff; not full GPU tile; no measured power.** Matched functional resources: 32-wave scheduler, four issue slots, 16 register banks with two read ports each, one write port, same 8-bit execution slice. Strict *equal consumed silicon area* was **not** enforced.

## Matched extracted observations

| Frozen metric | Gate | V296 pairwise | Serial one-hot |
| --- | ---: | ---: | ---: |
| Final cell area, µm² | ≤30,000 | 17,857.644252 | 18,953.830505 |
| Worst setup slack, ns | ≥+0.050 | **−1.047895 FAIL** | **−1.859922 FAIL** |
| Worst hold slack, ns | ≥0 | **−0.036622 FAIL** | **−0.019796 FAIL** |
| Slew violations | 0 | 0 | 0 |
| Capacitance violations | 0 | **3 FAIL** | **3 FAIL** |
| Completed detailed route | yes | yes | yes |

The candidate's observed area is **5.78345% lower** than the serial control and its worst extracted setup slack is **0.812027 ns less negative**. These are **infeasible implementation comparisons**, not a physically credible Pareto win. Candidate setup guard shortfall = **1.097895 ns**; serial guard shortfall = **1.909922 ns**. Both also fail hold and capacitance checks. A 3.5 ns clock is not closed by either design; a more favorable negative slack is not proof of improved achievable GPU Fmax.

The previous integrated *mapped* area difference was only 0.731714%, whereas final extracted cell area differs by 5.78345%. These are distinct implementation stages. Do not infer the extra difference is intrinsic arbitration savings without a matched backend attribution study.

## Reproduction and independent falsification

Download the **original** aggregate artifact from the run and extract `aggregate.tile_slice.json`. The preexisting `audit_tile_slice.py` reconstructs the paired results from full physical artifacts. Run `python3 research/v296/paired_slice_original_audit.py --self-test` then `python3 research/v296/paired_slice_original_audit.py --aggregate path/to/aggregate.tile_slice.json`. The additional checker pins the original numerical observations and frozen thresholds, independently recomputes area and slack differences, rejects altered measurements and unsupported GPU claims. It is an arithmetic/provenance cross-check, **not** independent re-extraction of SPEF/STA.

## Decision and next kill gate

**The original V296 integrated-slice feasibility hypothesis fails; no GPU speedup or physically feasible tile-level Pareto result can be claimed.** Same-clock RTL admission gain is 0%. Do not silently relax the frozen clock, change repair policies, change the serial baseline, or open prospective workload holdouts to rescue this result. V296 stays the *only mechanism under falsification*, not a validated mechanism. V287 remains retired.

Any future revised physical experiment must be a **new, prospectively frozen protocol**, run *both* contestants with identical disclosed timing/repair/load rules and independent audit. First diagnose actual post-CTS critical paths, hold and three cap violators; then test whether **both** can close timing/electrical constraints and whether the improvement survives strict equal-area resource accounting. If not, retire the integrated-performance claim. Only after that: measured integrated tile Fmax/power and unseen workload-level throughput/traffic/occupancy. No RTX-5090 equivalence claim is justified.
