# V296 joint area-packing / dependency / shared-port falsification (preregistered 2026-10-26)

**Evidence tier:** prospective synthetic resource-accounting experiment. Not RTL/physical closure, silicon throughput, power, or proof that a replicated tile fits. Only V296 is under test; V287 remains retired.

## Frozen resources and accounting

Prior *mapped balanced-return* areas: serial 9844.926 um^2/slice; V296 9286.592 um^2/slice. Under a hypothetical fixed area budget equal to **17 serial slices**, integer packing permits **18 V296 slices**. This is not yet a routed/equal-consumed-area tile. Both variants have 4 issue slots per slice, 16 banks per slice, 2 reads per bank, 2 operands per wave, and a **fixed global population W of one-outstanding-operation warps**. Serial latency L=1 cycle; symmetric operand-capture latency L=2. Same nominal 3.5 ns period is hypothetical because both physical implementations fail timing.

Ideal conservation envelope at matched clock: Q <= min(4N, W/L, B/m, R/2). The 18-vs-17 packing opportunity can exceed the **ideal serial 68 wave/cycle issue ceiling** only if W>136; it can reach the ideal 72 wave/cycle candidate ceiling only when W>=144. These are **necessary envelope conditions, not sufficient empirical predictions** and cannot prove no-win against a port-conflicted serial implementation. More warps or more area do not increase shared bandwidth B or global read capacity R.

## Prospective paired request replay

Implement a deterministic request-level simulator with each global warp assigned round-robin to N slices (17 serial, 18 candidate). Each warp's infinite conceptual request stream is generated independently of either policy from a fixed seed and warp ID; both variants consume identical per-warp request streams (possibly at different rates). A rotating per-slice priority scans ready warps and greedily admits at most four, subject to at most two read ports per bank per cycle. Issued warp becomes ready at t+L. No bypass, cache, branch divergence, or SRAM macro. Warmup 500 cycles; evaluate 4000 cycles; bank hotspot probability h, intra-wave same-bank probability p=0.2; default h=0.0. Global bandwidth is a separate capped fluid server, not an additional hidden per-slice port.

**Frozen cells** evaluated for both seeds 41719 and 41743: W=32, W=136, W=140, W=144, W=180, W=180 with shared useful-rate cap 25 waves/cycle, W=180 with candidate period +7%, W=180 with hotspot h=0.8. The default nominal clock ratio is 1.0. Shared-cap results must be reported in useful throughput, not raw issued waves. The +7% candidate-period cell must use feasible-clock *counterfactual* labeling.

## Predictions frozen before executing simulator

- W=32 is a strong predicted **no-win** regime because L=2 consumes scarce warp-level parallelism. W=180 distributed banks, unlimited shared bandwidth, is a predicted **win** regime from the extra hypothetical slice, assuming bank conflicts do not reverse the effect.
- W=180 with a shared cap 25 waves/cycle is predicted **no-win** in useful rate if both contestants exceed the cap. W=180 with candidate period +7% is predicted **no-win** at the physical-time rate if the observed equal-clock gain is less than 7%.
- W=136, 140, 144 and W=180/h=0.8 are **boundary/falsification probes**; do not relabel their outcomes as preregistered wins.
- Explicitly report ideal conservation bounds, issued and useful rates, per-slice warp distribution, cap saturation, and all negative results.
- Independent checker must test per-bank port conservation, per-warp cooldown, deterministic replay, exact low-warp throughput on a no-conflict control, and the area floor inequalities. Fail closed on mismatched resource counts or changed seeds.

## Decision

A successful synthetic result cannot rescue either failed 3.5 ns routed implementation. If physical constraints erase the area replication or feasible clock, kill the integrated-performance claim. Strongest independently optimized serial control, matched extracted timing/electrical checks, realistic shared bandwidth, actual switching, and unseen real workloads remain mandatory.
