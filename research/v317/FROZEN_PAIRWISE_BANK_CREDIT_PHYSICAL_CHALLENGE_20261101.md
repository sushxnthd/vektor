# Frozen V317 pairwise bank-credit implementation challenge (2026-11-01)

## Scope and evidence discipline
Keep the sole active V317 research branch and draft PR #34. The exact-cardinality selector and register forwarding are already rejected. This experiment is **a source-faithful implementation-cost challenge to the rotating-priority strong control**, not a new GPU architecture mechanism. The V287 and V296 historical evidence is not displaced. No change to bank ports, issue slots, operand count, warp semantics, or prior frozen holdouts.

## Mechanism and independent equivalence
Four request slots, 16 register banks, two reads per granted instruction and **two physical reads per bank per cycle**. A new pairwise-credit implementation will decide whether each of the two operand banks has capacity by counting hits against *previously granted* operands, instead of materializing 16-bit used-once/used-twice masks. If the two new operands are in the same bank, no earlier hit is permitted. Otherwise each bank permits at most one earlier hit. Fixed and rotating versions must produce exactly the same grants as the existing corresponding versions. The rotating implementation must pay for its phase state and operand permutation.

## Predictions frozen before RTL or synthesis
1. Functional equivalence: exhaustive 4 phases × 16 valid masks × 256 two-bank operand encodings = 16,384 configurations, plus 64 directed 16-bank configurations, 4,096 seeded random full-bank configurations, and reset/wrap checks. All grants must match an independent 2-reads-per-bank greedy oracle, not merely the source RTL.
2. Area hypothesis: the pairwise fixed and pairwise rotating versions each use fewer **Yosys generic cells** than their source-faithful counterparts under identical synthesis commands. This is a testable prediction, not an observed result. Logic depth may regress; report it without hiding.
3. Service equivalence: because the grants are functionally identical, any completion or traffic gain at the same clock and bank-port budget must be exactly zero. A nonzero synthetic service gain is a bug, not a discovery. The only potential benefit is hardware implementation cost or achievable clock, to be established separately.
4. Timing/no-go: a lower generic-cell count is not sufficient. If logic depth or mapped/routed timing deteriorates, do not promote a positive PPA result. Physical wire/load, fanout, standard-cell timing, power and tile area are not implied by generic Yosys counts.
5. Strong-baseline requirement: any area reduction that also applies to fixed priority is an RTL optimization, not evidence of a novel rotating-priority scheduling mechanism. Do not claim GPU IPC, RTX-5090 equivalence or architectural novelty.

## Verification sequence
Commit this protocol first. Commit synthesizable RTL, independent exhaustive testbench, reproducible matched Yosys workflow and cost parser next. Run hosted simulation/synthesis. Preserve failed CI, measured negative results and all synthesis limitations in a source-pinned report.