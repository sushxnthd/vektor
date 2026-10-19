# V234 — Adaptive last-operand collector retention (UNQUALIFIED)

Evidence class: analytic law and independently checked cycle model only. Exactly one active architecture mechanism.

**Bottleneck:** two operand reads to a single-port RF bank serialize unless the second operand is already in the collector.

**Mechanism:** retain last B operand in an existing 1-slot collector data/tag latch. Compare tag; hit bypasses RF read. Invalidate on writes. No extra operand buffer, RF ports, or bandwidth.

**Strongest simpler control:** equal 1-slot tag/data storage and one RF port, with static-pinned operand chosen by an *offline frequency oracle* from the full trace. Candidate is adaptive last-use. Static oracle can be superior on skewed IID traffic.

**Derived boundary:** h_D=P(B_t=B_(t-1)); h_S=max_b P(B=b); q=same-bank collision probability; m=independent memory/divergence stall cycles per instruction. G=(1+m+q(1-h_S))/(1+m+q(1-h_D))-1. Win requires h_D>h_S and q>0 before Fmax and power penalties.

**Frozen unseen cases:** 100,000 instructions, seeds 9127 and 9301: phase16 G>25%; iid8 |G|<2%; skew90 G<-2%. Memory extra cycles=8 suppresses throughput benefit. Collision q=0 eliminates throughput benefit, though read traffic can decline.

**RTL:** one 32-bit data latch, 6-bit tag, valid bit in both controls; compare + 32-bit mux; candidate updates on every accepted miss, control only on pinned-tag miss. Stale data must be invalidated on writeback.

**Physical gate:** functional equivalence -> RTL simulation -> synthesis -> max-cap/slew -> matched area/timing -> workload model -> wire/load sensitivity. No physical or RTX 5090 claim. V153/V156 remain electrically disqualified.

**Decisive falsification:** fail RTL semantics, equal-resource optimized prefetch control dominates, or physical timing/area/power overhead erases useful throughput/energy gain. If physical validation remains blocked after two substantive attempts, retire the kernel.

**Prior art:** operand reuse caches, operand collectors, and RF banking are established. This is a boundary hypothesis, not an originality claim.

**Integrated tile:** unchanged until physical qualification.
