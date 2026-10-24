# V296 prospective detailed-route / extracted-RC discriminator — frozen 2026-10-23 BEFORE execution

## Input evidence and immutability
The six-case third-round global-route experiment **passed its own preregistered gate** (run 39976579976; report `THIRD_ROUND_GLOBAL_ROUTE_RESULT_20261023.md`). The earlier two-round experiment **failed**, and must remain failed. The nominal original control has only +4.18 ps modeled setup margin, so this is a necessary next falsification. V296 remains the sole active mechanism. V287 retired. Workload holdouts sealed.

## Fixed comparison
Original controller, optimized one-hot control, and V296, each at nominal 1× and high 2× wire RC, **same RTL, toolchain, floorplan, 3.5 ns clock, I/O delays, output loads and three prior repair rounds** as the frozen third-round experiment. Do not modify the third-round flow or cherry-pick successful cases. For all six, append exactly one detailed route with default deterministic settings, and then perform calibrated Nangate45 OpenRCX extraction using the **revision-pinned** `rcx_patterns.rules` from ORFS commit `eda8e552974d47a12616294dddf4012d892548d3`. For high RC, multiply extracted resistance, ground capacitance and coupling capacitance by 2.0 **after extraction**; nominal uses 1.0. Export nonempty SPEF and final detailed DEF. No additional cell resizing or timing repair after detailed route; geometry changes are limited to routing.

## Frozen prospective predictions
1. **V296 will remain ≥10% smaller** than the smallest control at both RC settings (area unchanged absent extra cells).
2. **V296 will retain ≥+0.20 ns extracted setup-slack advantage** over the fastest control in both settings. This is a prediction, not an observed fact.
3. The nominal original control's +4.18 ps global-route margin is fragile; the all-case extracted setup gate **may fail** even if V296 remains advantageous. Preserve this as a negative result.
4. All six must complete detailed routing with **zero reported detailed-router DRC violations**, complete routed DEF, nonempty extracted SPEF, nonnegative extracted setup and minimum-delay hold slack, and zero max-slew/max-cap violations. The hold check is pre-CTS / ideal-clock and **does not establish post-CTS hold closure**.
5. Same-clock issue-throughput gain remains **0%** by RTL functional equivalence. Do not open workload holdouts on this experiment.

## Fail-closed decision
Independent checker must require all six files and audit tokens, zero detailed-router DRC, complete routes, nonempty SPEF and final DEF, finite extracted setup/hold and area, zero electrical violations, and positive area/slack dominance against **both** controls in **both** regimes. Check the 10% / 0.20 ns predictions separately. Any missing RC calibration, unsupported Tcl option, unrouted net, routing failure, extracted setup/hold/electrical failure, or DRC violation produces **DETAILED_PHYSICAL_GATE_FAIL**, never a provisional pass. If V296 loses either area or timing dominance in any regime, recommend retiring V296. Do not loosen the gate after observing results.

This is **open-source Nangate45 research PPA**, not foundry signoff. Full clock tree, post-CTS hold, antenna/IR/EM, independent signoff DRC/LVS, power, equal-tile-area alternatives, unseen workloads and integrated tile consequences remain separate mandatory gates. No RTX 5090-equivalence claims.

## Reproduction
Run `bash research/v296/run_detailed_route.sh` after pinned tools/platform installation. Evidence and checker are committed separately after this freeze. Preserve complete raw logs and all failures in the artifact.
