# V296 D4/D8 dynamic-RF routed transfer: frozen physical experiment (2026-10-27)

## Scientific question and evidence isolation
V296 pairwise bank admission remains the **only** active architecture mechanism. V287 and the static fixed-word deep-bank shortcut remain retired. Existing two-word extracted-RC feasibility and D4/D8/D16 mapped results remain immutable, and sealed workload holdouts stay sealed. This is a prospective **flop-array RF proxy**, not a GPU SRAM macro, full GPU tile, or RTX 5090 comparison.

## Frozen contestants, resources, and protocol
- Test both **D4 and D8 words per bank** (WORD_BITS 2 and 3), each with 16 banks, two **dynamically addressed** physical read ports per bank, one global write port, four issue slots, 8-bit data, 32 candidate waves, and identical operand-capture/return fabric.
- The sole contestant difference is the issue arbiter: V296 pairwise versus the optimized serial V295 core with `PREDECODE=0` **plus** the existing fifth-stage serial-favoring physical repair. Neither contestant gets extra ports, clock cycles, or a different RF.
- Reuse the frozen **symmetric 25 ps post-CTS hold-margin** intervention, the 260 x 260 um die / 240 x 240 um core, 45% placement density, 3.5 ns clock, 150 ps IO delays, 5 fF output load, 250 ps slew limit, fanout 16, CTS, detailed route, extracted OpenRCX **2x RC**, symmetric 250 ps setup repair, and identical physical scripts for both. Do not adapt these based on results.
- Require cycle-exact independent RTL oracle for D4 and D8, already hosted in #40527760514, and rerun as a dependency before physical trials. Yosys `check -assert`, full logs, DEF/SPEF, tool/library/source hashes, and original evidence artifacts are mandatory. Treat tool timeout as **censored**, never as an electrical pass.
- Require **both** contestants to satisfy final setup >= +50 ps, hold >= 0 ps, cap/slew/DRC violations all zero, area <= 30,000 um2. Then require V296 area at least 1% smaller and setup slack lead at least 50 ps. If either is infeasible, no matched Pareto claim; if both feasible but differences fall short, reject the proposed physical advantage.
- No relaxation of thresholds, selective seed choice, or new mechanism. Run both depths, retain negative results and independent checker.

## Preregistered physical predictions / falsifiers
D4 mapped: V296 12,960.584 vs serial 13,835.990 um2, saving **875.406 um2**. D8 mapped: V296 17,552.542 vs serial 18,782.260 um2, saving **1,229.718 um2**. These are *observations at the mapped evidence tier*, not routed predictions. Let `Hc(D)` and `Hs(D)` denote additional physical overhead. V296's area ordering survives only if `Hc-Hs < 875.406` at D4 and `Hc-Hs < 1229.718` at D8. A physical inversion is a direct falsification of the mapped-to-routed area-transfer hypothesis. Even a favorable ordering does not establish a throughput gain.

Prospective workload regimes (still sealed; do not evaluate in this experiment): **predicted win** only for high pair compatibility, high occupancy, and low shared memory/port pressure *if* the candidate gains feasible tile capacity or measured cycle time; **predicted no-win** for saturated external bandwidth/ports or identical feasible clock/capacity. Same-clock per-slice admitted waves are predicted **exactly equal**. A compact future boundary must include compatibility probability, mask/bank overlap, occupancy, port/bandwidth caps, physical area and control overhead and must transfer to unseen traces.

## Decision and limitations
This is the next hard gate after D16 mapped synthesis. A candidate-only pass, or two infeasible implementations, is **not** a matched physical win. All physical results remain proxy evidence until realistic RF macro, wire/load/clock replication, power, workload and independent prior-art checks pass. Preserve the single persistent branch and draft PR #13; do not touch Kernellum PR #119 or its prospective holdouts.
