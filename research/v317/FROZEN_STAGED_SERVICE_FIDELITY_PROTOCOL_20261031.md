# V317 adversarial staging-fidelity protocol (2026-10-31)

Status: prospective *model-comparison* predictions recorded before implementing the staged-service checker. This is an exploratory follow-up to the already inspected atomic model, not an independent GPU holdout.

## Hypothesis and frozen setup

The V317 atomic-mask model forces every source-bank read of an instruction to occur in the same cycle. A conventional buffered operand collector can collect independent operands across cycles. Therefore the synthetic 1.500x atomic coissue result is not evidence of a physical 1.500x speedup against a staged, equal-port baseline.

Retain the same 3 banks (A,B,C), one read per bank per cycle, at most 2 completed instructions per cycle, zero latency/overhead, unlimited pending operand buffers, full reordering and all operands initially ready. The staged comparator is given exactly the same per-bank ports and instruction-completion limit as the candidate. Each instruction may read different banks in different cycles. No cache-hit assumption.

Frozen workloads, in the order (AB,BC,CA):
- Predicted atomic-win (2,2,2): atomic 6 vs 4 cycles; staged **4 vs 4** cycles (gain 1.000x).
- Predicted atomic-no-win (0,3,3): atomic 6 vs 6; staged **6 vs 6** (gain 1.000x).
- Previously frozen transfer (2,1,3): atomic 6 vs 5; staged **5 vs 5** (gain 1.000x).

Lower bound on staged service cycles: max(ceil(N/2), max_b D_b), where D_b is number of requested reads at bank b. Independently verify a concrete schedule achieving the bound in each frozen case, with every required instruction-bank read exactly once, no extra reads, no per-bank overbooking and at most two newly completed instructions/cycle.

## Decision rule

If the strong staged baseline ties the hypothetical candidate on these workloads, retire the **atomic-only gain as an architecture-selection signal**; do not claim all realistic collectors tie. If the witness cannot be verified, mark the prediction failed. No new mechanism, RTL/PPA or GPU performance claim is permitted from this experiment. Next hard gate: bounded collector capacity, realistic operand readiness, compiler-guided scheduling, physical bank mapping, and measured SASS execution.

## Independence and provenance

Implement a separate witness validator that does not invoke the existing atomic dynamic-programming scheduler. The report must disclose the optimistic unlimited-buffer assumption and that these examples were selected after the atomic result was known.
