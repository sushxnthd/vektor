# Discovery Protocol V2: Vektor-063

## Claim state
- KNOWN (model): 062 treats strong quiescence ACK as an independent control path; it did not charge ACK traffic against the return data link.
- KNOWN (mathematical, conditional): if each completed transaction consumes one data and one ACK flit on a single 1-flit/cycle lane, asymptotic throughput cannot exceed 0.5 transactions/cycle without replays.
- BELIEVED: dedicated or aggregated ACK transport may improve tag retirement throughput in sufficiently occupied fabrics; actual PPA may outweigh gains.
- FALSIFIED (within synthetic model): an independent-ACK throughput estimate can be reused unchanged when ACK and data flits share one saturated lane.
- CONFLICTING: ACK-first and data-first scheduling have similar steady-state throughput but differ at low occupancy and finite horizons.
- ANOMALOUS: data-first at finite horizon sometimes exceeds the asymptotic ceiling slightly because completed transactions can have unretired ACKs.
- UNTESTED: quiescence-ACK generator correctness, dynamic NoC replay traffic, timing/area/power, actual V-Tile workload behavior, GDDR7 controller, compiler, raster, ray, and matrix capability.

## Experiment
Mechanism: return-link flit conservation under explicit packet replay and fence retirement.
Prediction: shared ACK/data 0.5 tx/cycle at zero replay with ample tags; dedicated ACK approximately 1.0.
Outcome: at 64 tags, 16,000-cycle zero-replay tests, shared ACK-first mean 0.499958 and dedicated mean 0.999750 transactions/cycle over three seeds. 108 primary cases, 18 holdouts; independent C++ model agreed on 96 single-copy cases.
Residual: shared -0.000042 and dedicated -0.000250 from steady-state ceilings, consistent with finite-horizon effects.
Assumptions weakened: 062's independent control path is not a neutral implementation detail; egress physical topology must be modeled.
Competing explanations: finite-window startup, ACK service policy, replay tails, tag occupancy, optimistic same-cycle dedicated ACK.
Uncertainty: high for physical architecture, low for specified deterministic model and conditional conservation law.
Cheapest next discriminating experiment: mapped synthesis of 063 arbiter and integrated quiescence ACK generation; vary ACK aggregation and egress lane width with equal flit budgets.

## Foothold
A reproducible capacity phase transition at shared ACK/data contention. This is an expected queueing conservation effect, not claimed as a novel hardware invention. Promote ACK transport cost to a first-class architecture bottleneck.

## Closed branches retained
062 independent-ACK assumption remains a useful idealized upper bound; do not discard its data. 060/061 generation wrap and replay counterexamples remain mandatory safety constraints.

## Next decisive action
Implement and verify a fabric-side quiescence ACK producer, including backpressure and delayed replay, then compare separate control, shared control, and batched acknowledgments under equal physical link budgets.
