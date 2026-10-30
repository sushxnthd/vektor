# V309 authenticated memory-address topology screen (frozen before full evaluation, 2026-10-30)

## Scope and no-promotion rule
This is an exploratory **workload qualification**, not a new hardware mechanism. Reuse the SHA-pinned 2020 V100 Rodinia SASS archive (SHA-256 aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1). The eleven families have already been inspected for other questions: **none are unseen architectural holdouts**. Do not change or reopen retired V287/V296/V297-V308. Maintain only draft PR #26.

## Frozen method
1. Parse active warp instruction rows, require exact format-0 explicit addresses, format-1 base+stride, or format-2 base+delta as documented by the Accel-Sim NVBit tracer. A compressed address record must reconstruct exactly one byte address per active lane. Reject malformed or out-of-range records and report failures rather than silently dropping them.
2. Restrict primary accounting to opcodes with LDG/STG/ATOM/RED stems, as a **proxy for global-memory operations**. Count and report all other memory rows separately; do not imply that every such opcode necessarily has the same cache path.
3. For each active global-proxy row and each lane's byte interval [address,address+mem_width), compute unique 32-byte sectors touched, 128-byte lines touched, and distinct requested byte count (union of intervals). Compare actual touched sectors with ceil(distinct requested bytes/32), the unattainable-in-general perfect-packing **layout** floor. Count format and width distributions.
4. Compare a strong free, ideal within-warp coalescer that issues exactly one 32-byte sector request per touched sector. Under fixed addresses, no alternative coalescer can use fewer distinct 32-byte sectors. Any difference from perfect packing is a potential **data layout** opportunity, not a hardware coalescer win.
5. Report per-family heterogeneity, 32-byte sector utilization, fraction of rows with packing slack, and a 64/128-byte granularity sensitivity. No cycle, bandwidth, latency, power or RTX 5090 claim is permitted.

## Frozen falsification and next gate
**Kill** any proposal to improve within-warp sector count by merely changing the coalescer for the same addresses: the ideal coalescer is already an exact fixed-address lower bound. Only consider a new physical mechanism if independent matched counters or validated simulation establish a bottleneck that survives the strongest equal-resource baseline. A real prospective win/no-win prediction must be frozen on **new workloads**, before seeing their outcomes. Do not use post-hoc Rodinia family selection as holdout validation.

## Source
Accel-Sim NVBit tracer implementation: https://github.com/accel-sim/accel-sim-framework/blob/dev/util/tracer_nvbit/tracer_tool/tracer_tool.cu
Purdue archive: https://engineering.purdue.edu/tgrogers/accel-sim/traces/tesla-v100/2020.03.18/rodinia_2.0-ft.tgz

## Pre-result parser compatibility amendment (2026-10-30)
The first authenticated archive decode failed closed at Needleman-Wunsch kernel-1 line 51. Its active mask was `00000001`, but format-0 encoded **32 lane-slot addresses**, including inactive lanes, rather than one address per active lane. The original rule "format-0 one address per active lane" was therefore false for this tracer revision. No memory-sector outcome was computed or inspected before this correction. Permit format-0 payloads of either 32 lane slots (select active lane indices) or exactly popcount(mask) compacted addresses. Continue to reject all other lengths. The correction does not change the global-proxy opcode classification, ideal-coalescer baseline, metrics or no-promotion decision. Preserve the failed CI run as negative parser evidence.

## Second pre-result compatibility observation
The subsequent fail-closed decode of the **same first record** established that format-0 contains exactly **16** address slots (active mask `0x00000001`), not 32. No workload metric was computed. Add a guarded 16-slot format-0 variant **only when every active lane index is below 16**; otherwise fail closed pending a documented lane-index mapping. Retain compact-popcount and 32-slot cases. This is a decoder compatibility correction, not an outcome-driven model adjustment.

## Third pre-result correction: refuse all legacy format-0 address topology
A second authenticated fail-closed decode reached BFS kernel-5 line 672, active mask `0x00010000` (only lane 16), but format-0 had **two** address tokens. The first case had one active lane and **16** address tokens. These incompatible cardinalities disprove both compact-popcount and fixed-slot interpretations without additional tracer-version documentation. The earlier 16-slot compatibility proposal is withdrawn **before any address-topology outcome was generated**. For scientific integrity, **exclude every format-0 row from address-sector calculations**, even those with seemingly decodable cardinality; retain exact counts of excluded rows and independently audit them. Format-1/2 rows may be analyzed only if their documented decoders pass strict cardinality and range checks. Report decoded-global coverage explicitly and refuse extrapolation to excluded rows. Any future verified format-0 decoder must be prospectively versioned and audited separately.
