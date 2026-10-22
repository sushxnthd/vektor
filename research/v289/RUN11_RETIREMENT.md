# V289 run 11: matched-resource falsification

Decision: RETIRE V289 (E0 software equivalence, not an electrical failure).

V289 selects the highest-priority request at each of two single-read-port banks, breaking ties by age. Its only added input is a one-bit criticality flag per request. The protocol already permits an equal-resource urgency-aware control with the identical bit, slots, ports, and priority rule. Relabeling the same bit as urgency yields exactly the same grant function for every legal input.

An exhaustive check covers 16 valid masks x 16 bank assignments x 16 priority masks = 4096 configurations. V289 differs from age-only selection in 584 configurations, but from matched urgency-aware selection in zero.

An independent synthetic dependency-chain scheduler evaluated 800 traces (50 seeds x four chain lengths x four background loads). V289 shortened critical-chain completion against age-first in 597 traces, but in all 800 traces the matched urgency-aware control gave identical makespan and critical-chain completion. For a 16-read chain with 32 background requests, age-first critical completion was 38 cycles, while both V289 and urgency-aware were 16; total modeled makespan was 38 for all three. Thus the apparent positive result is not a mechanism-specific improvement.

These are software results only. No V289 RTL simulation, synthesis, characterized STA, max-cap/slew, switching power, or integrated-tile claim follows. No physical evidence is being fabricated.

The existing V287 dual-warp fusion mechanism remains retired under its integrated RF-grant bound. It is not reactivated. The next active mechanism must deliberately search for a positive boundary law, but may not claim a breakthrough without equal-budget physical evidence.
