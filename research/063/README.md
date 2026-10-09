# Vektor-063: return-lane contention

**Discovery class:** DISCRIMINATION / CAPABILITY-BUILDING.

Hypothesis: Vektor-062's independent quiescence-ack path is optimistic when data and acknowledgments share one return lane.

Preregistered: one data response plus one acknowledgment per transaction imposes a shared-lane capacity ceiling near 0.5 transactions/cycle without replays. With mean replay count p, ceiling approaches 1/(2+p). Dedicated acknowledgments instead permit a data-lane ceiling 1/(1+p).

Synthetic model result: 108 paired configurations, 18 holdout checks, and 96 independent C++ comparisons. At 64 tags without replays, the shared ACK-first policy modeled about 0.500 transactions/cycle versus 1.000 for dedicated acknowledgments.

This is software modeling, not silicon or GPU-level evidence. A strong quiescence acknowledgment remains a fabric contract to implement.

Next: test synthesizable egress arbitration with backpressure, then implement fabric-side acknowledgment generation and timing/area comparisons.
