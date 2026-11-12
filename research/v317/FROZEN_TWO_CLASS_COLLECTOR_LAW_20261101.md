# V317: preregistered two-class collector-threshold law (2026-11-01)

Frozen **after** the initial bounded-collector pilot and its K=1 falsification, but **before** opening the new count holdouts below. The previous protocol is preserved unchanged, including its wrong K=1 prediction.

Restricted world: c=0 (only AB and BC), independent one-port banks A/B/C, two completions/cycle, all instructions initially ready, no dependency/clock/control costs, no bank-cache reuse, optimal admission and staged service. Baseline AB/BC; hypothetical candidate A/BC. K is the **same** number of collector entries in both designs.

## Derived exact prediction (restricted world only)

For N=a+b>0:
- If K=1, both finish exactly N cycles. One collector holds one instruction, and its two bank reads can happen in the same cycle. G=1.
- If K>=2, baseline finishes exactly a+b cycles because both instruction classes require the single B port. Candidate finishes exactly max(a,b) cycles: pair one AB and one BC each cycle, using disjoint banks A versus B/C, then finish the remainder. G=(a+b)/max(a,b).
- K=0 is unsupported. This says nothing about classes CA, real instruction latency, or physical implementation. If a=0 or b=0, gain=1 for all K.

This is a discontinuous occupancy boundary in the stated ideal model, not a GPU architecture law. The K=1 preregistered formula from the first protocol is explicitly **falsified**.

## Unopened holdouts
Check exact BFS schedules and independently replay traces for (a,b,c)=(4,3,0),(5,2,0),(1,4,0),(0,5,0), with K=1,2,3. Compare to the law with no fitting. Also test a,b in 0..4, excluding empty, K=1,2,3, with a state cap and honest failure reporting.

## Physicality gates
Any empirical win is an optimistic upper bound on benefit from a hypothetical B-read elimination, not a fabricated RF-cache hit or RTL result. The next hardware decision requires an implementable read elimination and a strong reuse-aware equal-resource baseline, including collector-area/clock penalties and actual bank mapping. No RTX 5090 performance claim.
