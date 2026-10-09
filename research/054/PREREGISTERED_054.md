# Vektor-054 predictions and falsification thresholds

Classification: CAPABILITY-BUILDING + DISCRIMINATION + EXPLOITATION.

**Timing disclosure:** This document was finalized after the local model-run grid and is NOT independently timestamped preregistration. It records the experiment's intended controls and falsification conditions for transparent reproduction. Do not describe the model results as a prospective public preregistered test.

Mechanism: two in-flight instruction slots; 3 register IDs per instruction; one read-request port; modeled response latency 2..12 cycles; explicit (tag, operand, reg) response identity. DEDUP=1 emits one request per distinct source ID and fans its return to all aliases. DEDUP=0 emits three requests. No RF banks, scoreboard dependencies, wave state, or real ISA.

Predictions:
1. At 0% source aliasing, DEDUP=0 and 1 have identical reads, completions and issued instructions.
2. With aliasing, DEDUP=1 reduces reads per completed instruction and can increase modeled completions in a read-limited regime.
3. Out-of-order tagged returns do not mix instruction operands.
4. Invalid returns raise sticky error and cannot mark operands received.
5. Synthesis may reveal a large area or timing penalty; no PPA advantage is presumed.

Grid: DEDUP={0,1}, alias={0,25,50,100}%, seeds={540054,540055,540056}, 2500 cycles each; 24 traces, 60,000 cycles. Deterministic offered instruction stream for each seed/alias pair; cycle-based randomized ready and return events.

Failure conditions: any model/replica disagreement, any difference in 0%-alias control, any malformed response incorrectly accepted, any RTL mismatch. Hardware efficiency claim requires actual equal-budget synthesis and realistic trace validation.
