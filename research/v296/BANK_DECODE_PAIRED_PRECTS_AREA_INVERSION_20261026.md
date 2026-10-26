# V296 decoded bank: matched serial pre-CTS completes, reverses mapped area order (2026-10-26)

**Decision: retain V296 only provisionally; decoded V296 is substantially better than the symmetric decoded serial at this intermediate checkpoint, but still has just 0.206 ps above the +50 ps setup guard. Neither CTS nor routed electrical signoff has been demonstrated, and the independently optimized fifth-stage serial control is excluded.**

## Original artifact provenance and independent audit

The paired jobs in [hosted run 40337484954](https://github.com/sushxnthd/vektor/actions/runs/40337484954) have now both completed successfully. Downloaded original ZIPs:
- Candidate artifact **12659251024**, SHA-256 `c5ec1f863b0cd23cc88fc9f0f468de87a90e1cb1dc0a3698e2af5d872a01cd2c`.
- Serial artifact **12664006227**, SHA-256 `52fd64575ac2124b171ecea3bcb27857b249589a11dc1624daeed179b33138b4`.

The [independent checker](bank_decode_paired_prects_independent_audit.py) verifies both exact ZIP hashes, all paired source/constraint manifests, matching Nangate45 platform digests, identical generated timing Tcl, explicit pre-CTS/not-routed tier, unique final markers, and final setup/hold/area/electrical metrics. Local original-ZIP audit passed. Deliberately corrupting the serial ZIP was rejected. Full numeric result is in [paired JSON](BANK_DECODE_PAIRED_PRECTS_RESULT_20261026.json).

## Paired *pre-CTS estimated-parasitics* measurements

| Metric | Decoded V296 | Decoded serial |
|---|---:|---:|
| Final intermediate area | **16,089.542143 µm²** | 17,301.969635 µm² |
| Worst setup slack | **+0.050206 ns** | −0.681592 ns |
| Worst hold slack | +0.112877 ns | +0.112877 ns |
| Max capacitance violations (reported final stage) | 0 | 0 |
| Max slew violations (reported final stage) | 0 | 0 |
| +50 ps setup guard | **PASS by 0.206 ps** | **FAIL by 731.592 ps** |

Candidate saves **7.00745%** intermediate area and has **731.798 ps** better setup slack than serial. This is a strong *stage-specific* relative difference, but not a physically feasible GPU advantage: the candidate guard margin is vanishingly small, and clock-tree synthesis, detailed routing, extracted RC, hold repair and electrical variation remain untested.

## Critical stage-dependent area inversion

The same decoder initially made V296 **2.79293% larger in mapped cell area** than decoded serial (10,426.402 vs 10,143.112 µm²). After the identical pre-CTS optimization and global-route diagnostic, V296 is instead **7.00745% smaller**. This is not contradictory: mapping area and physically optimized area are different evidence tiers, and the serial path required more physical repair. Do **not** use the mapped-only 17-serial/16-candidate replay to claim a physical tile outcome.

At the *intermediate single-slice area* only, a budget of 17 serial slices (294,133.484 µm²) could hypothetically hold 18 candidate slices (289,611.759 µm²), leaving 4,521.725 µm² or **1.5613%** spare relative to candidate aggregate. This is a sensitivity calculation, **not** a placed, routed or timing-closed replicated tile; 1.56% may be erased by shared interconnect, clock trees, macro geometry and buffering.

## Falsification and next step

1. Do not promote the 0.206 ps setup margin to physical timing closure. At this stage, a +0.206 ps adverse perturbation erases the +50 ps guard.
2. Do not claim dominance over the independently optimized serial fifth-stage control: it was expressly excluded by the matched flow manifest.
3. Next implement a paired **post-CTS/detailed-route extracted-RC** decoder experiment under unchanged constraints and area budget, including the strongest fifth-stage serial control. Require setup ≥+50 ps, hold ≥0, zero cap/slew/DRC. If the candidate fails, reject the decoder as a physical repair.
4. Once physical feasible clocks and tile costs exist, rerun frozen occupancy, bank-conflict, dependency and shared-bandwidth boundary predictions with the measured period ratio. Real workload holdouts stay unopened.

The separately preregistered decoded mapped-area synthetic replay is retained as a valid *mapped-only* counterfactual, not the physically controlling result. V296 remains the sole provisional mechanism, V287 retired, Kernellum PR #119 untouched. No RTX-5090 equivalence, measured GPU throughput or power claim.
