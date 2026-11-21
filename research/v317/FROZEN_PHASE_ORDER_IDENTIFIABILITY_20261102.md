# Frozen V317 phase-order identifiability and low-cost control challenge (2026-11-02)

## Status and evidence tier
Prospective test frozen before evaluator execution. The clean two-phase stream was selected in an exploratory search of 1,600 patterns; this protocol does not erase that selection bias. Synthetic finite-queue scheduler only, not RTL, SRAM, physical PPA, GPU IPC, or RTX 5090. Prior V317 electrical and equal-resource failures remain binding.

## Mechanism
Four candidate requests from an eight-entry FIFO, 2 reads/request, 2 ports/bank, oldest mandatory, four offered requests per cycle, output cap 4. Unbounded upstream backlog explicitly excluded from hardware capacity. Fixed two-phase sequence:
phase0 [(3,4),(1,4),(2,4),(0,0)]
phase1 [(3,1),(1,1),(3,3),(4,0)].
Warmup 500 cycles, measured 3,000 cycles, seeds 137, 271, 809; no replacement.

## New controls (same abstract resources, not equal silicon area)
- greedy: oldest then first feasible in FIFO order.
- reverse: oldest then newest-to-oldest feasible.
- degree: oldest then feasible requests ordered by ascending number of bank-overlap conflicts with other pending requests; tie FIFO order. This is a combinational heuristic requiring physical evaluation.
- exact_head: enumerate legal subsets containing oldest, maximize grants, oldest-first tie-break.
Strong comparator: highest aggregate completions among all three simple policies per regime.

## Frozen perturbations and predictions
1. clean: selected pattern unchanged. Predicted exact/simple >=1.05 (selection-conditioned positive control).
2. phase_flip_1pct: at each cycle independently choose opposite phase with probability 0.01. Predicted exact/simple >=1.02.
3. row_shuffle: independently shuffle four offered requests each cycle, preserving exact per-cycle bank-demand multiset. Predicted no-win exact/simple <1.05.
4. phase_random: independently choose phase each cycle with probability 1/2. Predicted no-win exact/simple <1.05.
5. cap2: clean pattern, output cap 2. Predicted no-win exact/simple <=1.01.

No changes to acceptance thresholds after measurement. If a predicted no-win fails, report it; do not redefine the hypothesis. If a simple control recovers most of the exact advantage, no distinctive architecture mechanism has been shown.

## Pre-outcome diagnostic
Lag-1 phase persistence P_same = fraction of adjacent offered rows with identical phase labels; row-order predictability O = fraction of row orderings matching canonical phase order. These use offered traces before scheduling. Clean: P_same=0, O=1; phase_random: P_same approximately 1/2; row_shuffle: O approximately 1/24. Mechanistic prediction: exact gain strongest when P_same low and O high. These are descriptive and not yet validated as a positive predictive law.

## Kill gates
No positive architecture promotion without independent nonselected-workload transfer, equal-resource low-cost RTL, legal routed timing/electrical, finite-buffer/backpressure throughput, area/power/clock/wire/load sensitivity, and reproducible audit. Negative results must be preserved. Keep existing branch and draft PR #34.
