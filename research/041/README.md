# SCHED-RF-PRIORITY-041 — model-level arbitration finding (2026-10-08)

**Evidence classification:** Python cycle-model and independent exhaustive checks only. No RTL simulation, synthesis, PPA or silicon measurements. Main branch unchanged.

## Baseline source contract
Reviewed `rtl/vtile/steal_warp_scheduler.sv`, `rtl/vtile/rf_bank_arbiter.sv`, and `rtl/vtile/issue_control.sv` on main, 2026-10-08. The arbiter iterates slots 0..3 in fixed order; scheduler RR pointers advance only on accepted issues.

## Preregistered predictions and outcomes
- P1: In all-same-bank, all-ready, dual-read contention, fixed slot priority issues only partition 0, while rotation spreads issue across partitions at identical 1.0 IPC. **SUPPORTED in cycle model:** 24/32 waves never issue with fixed priority; 0/32 starve with rotation, Jain fairness 0.25 -> 1.00.
- P2: Rotation can reduce modeled IPC. **SUPPORTED:** 23 losses, 26 wins, 95 ties in 144 paired equal-budget configurations. Largest loss -0.246875 modeled IPC in periodic four-hot regime. Do not claim universal throughput improvement.
- P3: Bank admission remains feasible. **SUPPORTED:** 35,426 valid randomized comparisons (40,000 draws; duplicate-wave candidates excluded) and 16,384 exhaustive reduced-bank comparisons; 0 mismatches.
- P4: Rotation alone does not guarantee fairness under arbitrary downstream replay. **SUPPORTED by adversarial counterexample.**

## Selective-replay counterexample
All 32 waves ready, both operands read bank 0, slot 0 permanently rejected downstream:
- Fixed priority: 0.0 modeled IPC.
- Rotate *only on successful acceptance*: 0.0 modeled IPC (phase freezes on rejected slot 0).
- Rotate on an enabled *attempt*: 0.75 modeled IPC, with slots 1–3 each contributing 480 accepts over 1,920 measured cycles. Eight waves in partition 0 remain unserviceable by construction. This is **not** universal fairness.

Under periodic global issue disable (1 cycle in 17), rotation-on-attempt freezes phase during the disabled cycles; measured IPC 0.941145833, with 0 starved waves for the all-same-bank case. This distinguishes global backpressure from per-slot replay.

## Experimental scope
432 model configurations (6 bank regimes × 3 cooldowns × 4 seeds × 2 periodic eligibility regimes × 3 policies), 1536 cycles each, 256 warmup; plus 8 replay scenarios of 2048 cycles each, 128 warmup. 4 issue slots, 16 RF banks, 2 read ports/bank, 32 waves, 4 partitions. Python source and exploratory RTL are in the separate reproducibility bundle pending repository upload. No physical performance or novelty claim.

## Discovery Protocol V2 world model
- KNOWN (code inspection): fixed RF arbitration order and acceptance-gated partition pointers in main.
- BELIEVED (model): rotation-on-attempt reduces phase deadlock under selective replay.
- FALSIFIED (model): acceptance-only phase rotation guarantees progress under selective replay.
- ANOMALOUS: 23/144 equal-budget comparisons lose IPC with rotating priority despite improved fairness.
- CONFLICTING: modeled progress versus unknown synthesis cost, combinational timing and integration semantics.
- UNTESTED: actual RTL simulation, Yosys area, STA frequency, physical implementation, system workloads.

**Single next decisive action:** Run RTL differential simulation with Icarus/Verilator on a research branch, then Yosys synthesize fixed and rotating arbiters under equal constraints. Integrate only if fairness gain survives and PPA tradeoffs are acceptable.

## 5090-class gates
Compute, tensor, graphics/raster, ray tracing, memory, frequency/area/power, and software stack: **INCONCLUSIVE**. A scheduler model result is not GPU equivalence.
