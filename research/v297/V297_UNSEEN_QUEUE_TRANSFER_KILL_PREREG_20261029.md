# V297 independent queue-transfer kill holdout (frozen before evaluation, 2026-10-29)

## Motivation and status
The three-way registered-shell physical experiment has completed at SHA `41a9291b` in [run #40775325841](https://github.com/sushxnthd/vektor/actions/runs/40775325841). The independent audit found all three controllers routed with clean setup, hold, capacitance, slew and DRC. The unrestricted max-pair control was 340.480005 um2 versus compact V297 358.035990 um2, with 2.944061 ns versus 2.911081 ns setup slack. These are physical **arbiter-macro** results, not integrated GPU throughput.

The last missing V297 stop condition is a **fresh prospective persistent-queue transfer** against the strongest same-resource max-pair control, without selecting a favorable demand regime after observing outcomes.

## Frozen evaluator
Reuse the unmodified `research/v297/v297_persistent_queue.js` exported `runOne` and `optimal` functions. Same 3-job candidate window, 2 issue slots, 16 banks, 2 read ports per bank, 64-entry finite FIFO, 1,000 warmup cycles and 20,000 measured cycles. The `oracle` is a physically implemented unrestricted max-pair RTL policy, not a hypothetical extra-resource machine. Existing generator, tie-breaks and cooldown semantics are frozen. Fresh independent seeds: **[17401, 17417, 17431, 17443]**.

## Prospectively selected unseen transfer combinations
All are untested regime/rate combinations in the original 7-row queue experiment:
1. `motif3_burst37`, arrivals=3 (saturated burst, predicted no V297 win).
2. `uniform16`, arrivals=3 (high-occupancy, predicted no V297 win).
3. `hot`, arrivals=1 (port bottleneck, predicted tie).
4. `motif3_burst37`, arrivals=1 (light occupancy, predicted tie).
5. `hot`, arrivals=3 (saturated bank, predicted tie).

## Hard stop
If the max-pair policy matches or exceeds V297 completed throughput on **all five frozen transfer rows**, and does not increase drops materially (strict tolerance 0.0001 completed waves/cycle and 3 drops over 20,000 cycles per seed), retire V297 as a positive architecture-performance candidate. A single V297 transfer win outside tolerance requires inspecting queue fairness and tail behavior; it does not override matched physical controls. Preserve negative findings. Do not relabel the matched 3.5 ns macro result as a GPU speedup.

## Non-interference
Keep V297 research branch and PR #14 until the stop verdict is committed; do not restart retired V287/V296. Kernellum PR #119 and its prospective holdouts remain untouched.
