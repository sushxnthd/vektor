# Vektor-049 research: finite RF response bandwidth and scoreboard

Date: 2026-10-09. Classification: DISCRIMINATION / CAPABILITY-BUILDING / SURPRISE.

This is an independently replicated **software model**, not RTL, synthesis, or silicon evidence. The main-branch Vektor RF arbiter accepts two operands/request; this exploratory collector supports three source operands per instruction. No RTX 5090-class gate is passed.

## Frozen predictions and measured simulation

1. H1: With three reads/instruction, the modeled steady-state ceilings include R/3 IPC for R returned operands/cycle and 2B/3 IPC for B banks with two reads/bank/cycle. At B=1,L=2,Q=64, changing R=2 to R=16 gives 0.664 -> 0.664 IPC (18/18 paired ties). At B=16,L=2,Q=64, it gives 0.67339 -> 4.000 IPC; the first number includes warmup boundary effects.
2. H2: With Q outstanding reads and read latency L, an idealized steady-state ceiling is Q/(3L) IPC. At B=16,L=8,R=16, Q=8 gives about 0.330 IPC, Q=64 gives 2.617–2.668 IPC across dependency fractions; all 18 paired configurations improve.
3. H3: Phase-dither is not a robust general 32-wave optimization. Across 648 paired cases: mean relative +0.396%, 387 wins / 196 losses / 65 ties; negative cases preserved.
4. H4: All modeled operand values and instruction identities remain consistent; no bank or queue overflow. 1,944 original + 1,944 controlled paired + 768 response-policy simulation runs and 216 exact independently reimplemented Python/C++ reduced-domain traces produced zero reported disagreements.
5. 049C response-order discriminator: completion-aware return vs FIFO over 384 paired cases: mean relative IPC **-0.176%**; 89 wins / 119 losses / 176 ties, despite mean instruction latency -0.143 cycles. No general adoption.
6. 049D anomaly control: R=2 short-window 674/1000=0.674 IPC vs long-window 32672/49000=0.666776 IPC; short-window overshoot is consistent with warmup prefill, not extra physical return capacity.

## Discovery Protocol V2

- KNOWN (within model): response conservation, bank capacity and tagged operand identity are enforced; 216 reduced-domain exact Python/C++ replication cases agree.
- BELIEVED: return bandwidth and outstanding queue storage can become first-order bottlenecks once RF bank conflicts are reduced; no hardware magnitude claim.
- CONFLICTING: 047's favorable phase-dither regime versus 048/049's occupancy-dependent weak or negative 32-wave results.
- FALSIFIED: unconditional phase-dither adoption; treating unlimited RF return bandwidth as harmless; assuming improved response latency necessarily increases throughput.
- ANOMALOUS: finite-window IPC overshoot (explained by prefill), and latency/throughput reversal under completion-aware response arbitration.
- UNTESTED: RTL data storage, response queue, replay, scoreboard integration, compiler-generated traces, physical RF write ports, synthesis PPA, matrix/raster/RT and broad GPU workloads.

Explorer: joint Q/R/bank design. Skeptic: synthetic workloads, no RF writes or physical area. Experimentalist: paired traces and exact replay. Analyst: negative cases preserved. Anomaly Hunter: boundary effects and response-order reversal. Prior-Art Auditor: operand collectors and Little's law are prior art. Replicator: 216 exact reduced-domain cross-checks. Theorist: under the model, steady-state IPC <= min(4, 2B/3, R/3, Q/(3L)) before dependency constraints.

The 049C preregistration's run-count arithmetic was incorrect: the frozen grid generated 768 runs / 384 pairs, not 384 / 192. This correction is post-experiment and preserved here.

## Next decisive action

Build tagged 32-wave operand-collector/response-FIFO RTL with replay and scoreboard, run differential verification and equal-budget Yosys synthesis, then test compiler-generated instruction mixes. Do not change Vektor-1A targets based on this synthetic result.

Complete reproducibility files (C++17, Python, preregistrations, raw CSV, JSON, SHA256) are preserved in the Vektor-049 package prepared in the research run. GitHub integration of source is tracked separately; this document alone is not sufficient to reproduce all runs.
