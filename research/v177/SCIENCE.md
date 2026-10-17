# V177 SCIENCE ledger

Question: Does the V153 cutset retain its mapped timing advantage over V151 as external operand arrival grows?

Frontier: V156 mapped OpenSTA measured -2.93 ns versus +1.65 ns slack at 0.05 ns input delay. V174-V176 supplied bounds, not the actual sweep.

Objective: Seven matched arrival delays, report timing and area-delay reversal, setup failures, and critical-path migration.

Strongest baseline: V151 buffered, same mapping/library, one lane and two-cycle interface. Area differs, so no equal-area claim.

Mechanism: input-origin cutset critical path should lose setup margin with increasing operand arrival, unlike initially register-origin V151.

Falsification: baseline mismatch, monotonicity failure, or measured path transitions inconsistent with the hypothesis.

Publishable threshold: independent reproduction, novel mechanism, equal-area comparison and unseen workloads; timing sweep alone is not a discovery.

Architecture threshold: a measured constraint that changes V-Tile operand staging or a robust >=10% gain with <=5% mapped-area penalty and equal throughput.

Kill: after three uninformative substantive runs, reformulate around operand staging or response credits.

Evidence: unplaced mapped single-lane OpenSTA only.
