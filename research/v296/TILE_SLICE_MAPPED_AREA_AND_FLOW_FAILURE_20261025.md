# V296 integrated RF-slice first mapped-area result and physical-flow failure (2026-10-25)

**Evidence tier:** verified hosted RTL equivalence plus paired Nangate45 **mapped synthesis**, NOT a routed or extracted physical result. This is a bounded negative/limitation of controller-to-slice area extrapolation.

## Exact matched integration

The preregistered [integration protocol](TILE_SLICE_PHYSICAL_PREREG_20261025.md) preceded the RTL and physical jobs. Both variants share the same 32-wave scheduler, four issue slots, 16 banks, two read ports per bank, one global write port, 16 x 2 x 8-bit flop RF, bank-to-operand routing and registered 8-bit execution per slot. Only V296 pairwise arbitration versus the optimized serial one-hot arbiter differs.

[RTL verification run 40156284582](https://github.com/sushxnthd/vektor/actions/runs/40156284582), job `121058271709`, **PASSED**: 2,048 randomized/adversarial cycles, 4,096 pre/post-clock checks, 6,589 admitted slot-events, no V296/control output mismatches, no >2-read/bank violations, and no independent direct-index RF oracle mismatches. The initial attempt [run 40156226148](https://github.com/sushxnthd/vektor/actions/runs/40156226148) failed compilation due to the reserved SystemVerilog keyword `table`; that code defect was corrected before this passing run.

## Paired mapped synthesis, identical integrated resources

From the **original paired** hosted [run 40156284582](https://github.com/sushxnthd/vektor/actions/runs/40156284582), independently downloaded original job archives `12584531365` (pairwise) and `12584820670` (serial one-hot), and inspected `*.synth.log`:

| Nangate45 mapped cell area | V296 pairwise | Optimized serial one-hot |
|---|---:|---:|
| Integrated slice, um2 | **10032.190** | **10106.138** |
| Pairwise absolute saving | **73.948 um2** | reference |
| Pairwise relative saving | **0.731714%** | reference |

Both synthesis jobs completed before physical implementation. This is an **observed sub-1% whole-slice mapped-area saving** under a small flop-RF slice, not the historical 14.35% *post-CTS controller-only* area saving. Different synthesis/physical stages and netlist optimization prohibit directly subtracting those percentages. This already warns against multiplying controller area percentages into tile claims.

The frozen **>=1% integrated area-saving** threshold is **not met at the mapped-synthesis stage**. The preregistered acceptance threshold applies to **post-CTS extracted integrated cell area**, so the final gate remains **pending** rather than retroactively failed.

## Physical-flow error and exact repair

The original pairwise and serial physical jobs both terminated **before floorplanning**, with OpenROAD `IFP-0011 use -site to add placement rows`. Their generated Tcl incorrectly placed the `-site FreePDK45_...` option on the new marker's `puts` line, leaving `initialize_floorplan` without `-site`. This is a **flow-generation bug, not an architectural electrical or timing failure**. The original failure artifacts and logs are preserved under the run above; no physical timing/area verdict is inferred from them.

The generator's exact-match replacement was repaired in commit `e91b21aa242bdaf8b69350c8fc823123eb376d3a` to preserve the original Nangate45 placement site. The corrected [new physical run](https://github.com/sushxnthd/vektor/actions/runs/40156470550) is separate and must pass the independent fail-closed checker before any extracted physical claim.

**Decision:** V296 remains provisional and sole active mechanism; V287 retired. Same-clock admission improvement is **zero**, full GPU-tile Fmax, strict equal-consumed-area reinvestment, real GPU workload speedup, power and unseen workload validation remain unestablished. If the corrected post-CTS integrated Pareto gate fails, record it as a genuine bounded falsification rather than selecting a new floorplan or weaker control.
