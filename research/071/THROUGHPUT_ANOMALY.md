# Vektor-071 throughput harness falsification (2026-10-10)

Classification: SURPRISE / DISCRIMINATION. All figures are synthetic software-model results, not GPU throughput.

## Mechanism and preregistration
Initial prediction: for service probability s and physical-copy duplication probability c, logical throughput under saturation is bounded asymptotically by s/(1+c), assuming the *admitted* mix has duplication probability c.

## Unexpected residual and root cause
At s=0.8, c=0.5, depth=16, a first simulation reported 0.62122 transactions/cycle, apparently 16.5% above 0.53333 bound. Its admitted clone fraction was only 0.2870, despite 0.50086 offered clones. The harness **incorrectly resampled a rejected request each cycle**, effectively dropping large (two-copy) requests under backpressure.

This invalid result is preserved as negative evidence, not an architecture gain.

## Corrected experiment
The corrected valid/ready generator holds each rejected transaction and its clone bit stable until admission. Seed 7, 50,000 cycles, same queue and service budget:
- Correct logical throughput: 0.53360 transactions/cycle.
- Correct admitted clone fraction: 0.50322.
- Correct physical service rate: 0.80182 packets/cycle.
- Effective capacity bound from the observed mix: 0.53219 transactions/cycle (finite-run residual +0.00141).
- Invalid resampling baseline: 0.62122 transactions/cycle, with clone fraction 0.28705.
- Physical-copy conservation holds in both models, showing that conservation **alone** cannot validate a workload generator.

36 structured configurations plus six minimally guided exploratory probes cover depths 2/4/8/16 and nonstandard depths, service probabilities, and duplication rates.

## World-model updates
- KNOWN: a backpressured producer must retain its pending packet identity and copy count; otherwise admission statistics are biased.
- FALSIFIED: the 0.62122 result represents a valid throughput improvement at 50% duplication.
- ANOMALOUS: the original result appeared to exceed the expected capacity bound because admitted packet sizes were not representative of offered packets.
- BELIEVED: capacity bounds must use admitted traffic mix, and offered/admitted mix must both be reported.
- UNTESTED: realistic multi-source fairness, ACK/data contention, and router physical timing.
- Cheapest discriminating experiment: RTL-ready/valid randomized driver with stable payload assertions and occupancy histograms.

No novelty claim: this is a verification-methodology correction.
