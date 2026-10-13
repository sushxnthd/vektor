# V155 ARCHITECTURE ledger

Affected block: Wave32 FP32 finisher downstream of multiplier and operand collector.

Build: Implemented two-stage buffered V151 control. Both candidates passed 24,220 oracle vectors with tags, masks, and backpressure. Open Nangate45 mapping completed for one lane.

Mapped area: buffered 8043.574 units (6427 cells); cutset 8029.210 units (6205 cells). Both map to 161 DFFR_X1. No physical timing, placement, power, or clock claim.

Decision: keep V151 functional baseline and V153 cutset candidate. Neither is adopted until mapped critical delay and system throughput are measured. Next build task: scoreboard/writeback integration, then realistic compute, memory, divergent and tensor workloads.

Evidence: passing run 38466588630, raw artifact 11848618881. Initial run 38466125786 failed on post-map checker plumbing and is preserved. No RTX 5090-class equivalence claim.
