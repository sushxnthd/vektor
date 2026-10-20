# V243 frozen protocol (2026-10-20, before experimental evaluation)
Mechanism: four-input one-output response arbitration, prioritize a final outstanding fragment (count=1), bounded-age fairness then round-robin.
Strongest equal-resource control: shortest-remaining-fragments-first (SRF), using identical count metadata, 4 candidates, 1 output, collector slots, buffering, fairness and clocks. Other controls: age-first and round-robin.
Law: completed warps/cycle <= min(response capacity per warp, K / mean collector residence cycles).
Positive holdout seed=243101, K=4, interleaved high-variance fragment counts, high offered occupancy. Negative holdout seed=243102, K=4, single-fragment warps, saturated return bandwidth. Direction tolerance <=2%; report uncertainty. Do not tune to holdouts.
Falsification: retire if SRF equals/exceeds candidate throughput at equal resources, or electrical qualification fails. No physical claim without RTL simulation, synthesis, electrical max-cap/slew, matched STA/area and wire/load sensitivity.
No RTX 5090 equivalence claim.
