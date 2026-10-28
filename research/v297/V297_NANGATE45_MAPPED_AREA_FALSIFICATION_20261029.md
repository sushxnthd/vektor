# V297 matched Nangate45 synthesis: original RTL dominated (2026-10-29)

**Verified hosted run:** [GitHub Actions 40754097807](https://github.com/sushxnthd/vektor/actions/runs/40754097807), `reproduce` job SUCCESS. It independently reproduced original synthetic experiments, finite-queue and phase tests, Markov-law failures, and 11,664-case max-pair dominance; passed the 17,832-cycle clocked Python/Verilog oracle for all four RTL contestants; and mapped each under the **same pinned Nangate45 typical liberty** from OpenROAD-flow-scripts revision `eda8e552974d47a12616294dddf4012d892548d3`.

| RTL contestant | Generic cells | Generic path levels | Nangate45 mapped cell area (µm² proxy) |
|---|---:|---:|---:|
| V297 original priority/rescue | 159 | 24 | **138.320** |
| V297 compact equivalent max-pair/cooldown | 146 | 12 | **126.882** |
| Unrestricted exact max-pair (no cooldown) | 137 | 11 | **116.508** |
| Cycle-rotating serial, dynamic-index implementation | 449 | 30 | **370.272** |

The compact same-behavior V297 implementation reduces mapped cell area by **8.27%** relative to the original V297 RTL and halves its unmapped generic logic depth. It is clock-for-clock grant-equivalent on all 17,832 hosted sequential tests and on the independent 11,664-case small-bank exhaustive check. The original implementation is therefore **dominated on matched mapped-area and generic-depth proxies** and must not be used to claim a hardware advantage.

The unrestricted max-pair controller is another **8.18% smaller** than the compact cooldown variant, but it has different fairness behavior. Its same-request admission count is never lower than V297, and exceeds V297 in 60/11,664 small-bank cases, all when cooldown is active. This does not establish superior persistent-queue latency or starvation. The rotating RTL is demonstrably a poor area implementation because of dynamic indexing; its mapped area must not be used as a strong area baseline without an optimized static implementation.

**Important timing caveat:** The post-liberty `ltp` command reports path length 0 because technology cells are treated as opaque in that pass. It is **not a zero-delay result**. The only meaningful depth proxy is the prior generic-gate LTP. There is no liberty-timed STA, placed route, extracted RC, hold, slew, capacitance, DRC, clock tree, or measured power. This is a **mapped-cell-area result**, not a physically feasible GPU tile.

## Post-outcome physical protocol amendment

The original physical preregistration `V297_MATCHED_PHYSICAL_KILL_PREREG_20261029.md` is preserved unchanged. Based on the newly opened mapped-area falsification, **promote the compact equivalent RTL as V297's sole implementation candidate for the next physical experiment**, keeping the original RTL as a negative implementation control. This does not introduce a new architectural mechanism, alter any workload prediction, or relax any clock, area, electrical, or fairness gates. Continue to compare against both optimized rotating serial and unrestricted max-pair; additionally test a fairness-matched max-pair implementation if its policy differs. If the compact design fails matched routed timing/electrical feasibility or a strong simple baseline captures the same performance at lower physical cost, retire V297.

## Scientific decision

V297's original RTL implementation is **killed as an optimization candidate**. The *mechanism* survives only as a provisional, classical-compatible-pair scheduling experiment; novelty is unestablished and physically credible speedup remains unproven. Do not claim RTX-5090 equivalence or GPU performance from these results.
