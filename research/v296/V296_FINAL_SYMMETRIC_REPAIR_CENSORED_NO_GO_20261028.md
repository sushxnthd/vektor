# V296: final symmetric upstream-repair evidence and bounded no-go (2026-10-28)

## Source and protocol
- Frozen preregistration: \`V296_SYMMETRIC_UPSTREAM_REPAIR_PREREG_20261028.md\`.
- GitHub Actions run: https://github.com/sushxnthd/vektor/actions/runs/40718719600
- Original evaluated head SHA: \`a62a79744acea3eee91376536e723bbb58fbea5d\`.
- Pairwise artifact ID \`12835775317\`, ZIP SHA256 \`fb607ec0d632662ef60da23ac70a914cf60c04a9f113e7a5604df54235f62ee7\`.
- Optimized serial artifact ID \`12835790308\`, ZIP SHA256 \`404ea1a9e98a5348009c67ed31044cdf7610a7a1b9927e6e9da6c83e4eeb58ea\`.
- Independent aggregate artifact ID \`12835795501\`. It correctly returns \`INCOMPLETE_NO_TILE_PHYSICAL_CLAIM\`, with no matched comparison.
- Independent ZIP audit: \`python3 research/v296/v296_final_repair_forensics.py PAIRWISE.zip SERIAL.zip --self-test\`. Original downloaded artifact ZIPs passed digest validation, stage provenance and negative-control mutation checks. The script is stdlib-only; its outputs are **forensics, not signoff**.

## Observations
Both contestant Actions jobs ended with **exit code 124** after the frozen **75-minute timeout**. The GitHub jobs themselves show "success" because the wrapper deliberately captures the nonzero physical tool exit code and uploads evidence. This is NOT a physical pass.

| Metric / stage | V296 pairwise | Optimized serial (fifth-stage) |
|---|---:|---:|
| Original RTL and repair Tcl | Same SHA | Same SHA |
| Upstream intervention executed before detailed route | Yes | Yes |
| Post-CTS/global-route estimated area, µm² | 19,657.399264 | 20,647.984655 |
| Post-CTS/global-route reported cap/slew violations | 0 / 0 | 0 / 0 |
| Detailed-route stage at timeout | 0th iteration, 90% progress | 1st iteration, 10% progress |
| Last **completed intermediate** detailed-route violation count | Unavailable | 33,077 (after 0th iteration) |
| Final extracted-RC setup/hold | Unavailable | Unavailable |
| Final DRC / SPEF | Unavailable | Unavailable |
| Physical feasibility | **Unestablished** | **Unestablished** |

The pre-detailed-route estimated-area difference is **990.585391 µm²**, or **4.79749%** relative to the serial control. It is not routed area, power, or tile-level throughput. Intermediate detailed-route violations are **not** final DRC violations. Both logs contain OpenROAD \`RSZ-0062 Unable to repair all setup violations\` warnings, but the warnings alone do not quantify final timing or prove infeasibility.

The detailed-route logs show a large routing burden. Serial reached 33,077 intermediate violations at the end of its first routing iteration and was 10% through the second when killed. Pairwise reached 90% of its first iteration. Neither produced a completed extracted-RC result. Thus this is a **matched censored experiment**, not evidence that one candidate physically defeats the other.

## Falsification and stop decision
The prospectively frozen positive gate requires **both** complete routed implementations with +250 ps setup guard, nonnegative hold, zero cap/slew and DRC, <=30,000 µm² and a matched physical Pareto lead. That gate is **not met**. No more post-hoc relaxation or asymmetric routing retries are permitted under this hypothesis.

More decisively, the independently checked arbitration pathwise-coupling result establishes that V296 and optimized serial admit identical waves on identical request traces at matched clock/latency. Under those conditions, the **exact workload issue-throughput gain is zero**, including both predicted win and no-win demand regimes. The frozen tile budget fits only one slice of either completed predecessor. Therefore, even an isolated area saving cannot support a claimed GPU throughput gain.

**Research decision:** Reject the *V296 integrated GPU performance-win claim*. Preserve V296 as a negative architecture result in draft PR #13, not as a validated or production-feasible GPU mechanism. This is a **program-level no-go under the current evidence and resource constraints**, NOT a mathematical proof that V296 can never be physically routed. Any successor must be separately preregistered, prior-art audited and tested against a truly matched resource baseline; do not resurrect V287 or continue unconstrained V296 repair sweeps.

Kernellum PR #119 and its prospective holdouts are unchanged. No RTX-5090 equivalence, silicon PPA, GPU performance, energy saving, or final DRC claim.
