# V151 SCIENCE ledger — 2026-10-14

## Active architectural research kernel
**Question:** Can a bounded signed-tail FMA finisher preserve exact binary32 RNE and exception flags with materially lower implementation cost than V150's 555-bit exact-wide reference, while retaining the operand-collector/dataflow constraints needed for a high-throughput V-Tile?

**Frontier / best-known:** V150 exact-wide golden RTL passed 16,916 oracle vectors. Full fused FMA and guard/round/sticky arithmetic are established prior art. V150 is a correctness reference, not a competitive hardware baseline. No original scientific mechanism is claimed.

**Exact objective:** zero bit/flag mismatches on frozen V150 plus V151 boundary corpus; synthesizable bounded RTL; compare generic Yosys cell counts and depth, then technology-mapped area/delay under equal lane count and clock targets. Later: IPC/energy across compute-, memory-, and divergence-limited kernels.

**Strongest equal-resource baseline:** same-lane V150 reference for correctness only; an independently validated public pipelined FMA of comparable latency, technology library, lane count and RF/collector capacity is still required for PPA/performance claims.

**Mechanism hypothesis:** leading-align the dominant term in W=64 bits; when the weaker term lies below the window, track its sign and nonzero tail. If the tail opposes the signed integer sum, subtract one from the integer magnitude before guard/sticky rounding. This distinguishes exact ties from slightly-above/below-half cases without 555-bit alignment.

**Quantitative prediction:** for all valid finite binary32 operands the dominant 48-bit product or 24-bit addend is exact in a 64-bit window. Only one operand can have a discarded tail. Thus bit/flag error count must be 0, including cancellation and subnormal transitions. Compared with V150, generic arithmetic width falls from 555 to 64 bits; this is NOT a 8.67x silicon-area prediction.

**Decisive falsification:** any mismatch on exact oracle or independent libc fmaf; a case where both terms have nonzero tails, or the signed truncated sum vanishes while tail remains; synthesis timeout/logic loops (engineering failure); mapped area-delay not competitive with a public FMA (architectural falsification).

**Publishable success threshold:** original architecture-relevant mechanism after novelty audit, matched mapped PPA and performance, frozen protocol, independent checker, unseen workloads and physically meaningful efficiency gain (preregister >=5% Pareto-relevant improvement).

**Architecture-relevance threshold:** full-range FMA plus tagged writeback/scoreboard integrated into a tile; at least >=5% improvement in area-normalized throughput or energy at equal resources without >2% workload regressions.

**Kill condition:** three substantive runs without an improved physical gate, mechanism boundary or new architectural constraint; replace with the next highest-information bottleneck.

**Evidence class:** V150 reference: RTL simulated. V151 Python bounded prototype: locally modeled (116,916 exact-oracle comparisons for W>=50; not independent RTL evidence). V151 RTL: 24,220/24,220 exact-oracle vectors passed; 5 Wave32 integrated directed transactions passed. Generic synthesis: 14,459 cells, 383 logic levels. Mapped PPA remains open. The prior-art claim remains NOT NOVEL. ARCH HDL (2026) reports a formally verified bounded 98-bit FMA with mapped timing; CVFPU/HardFloat are public baselines. No equal-resource superiority claim.
