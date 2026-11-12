# V309: source-conditional global-load line-reuse envelope (preregistered 2026-10-30)

**Status:** qualification/falsification only, no hardware mechanism promoted. Preserve V309 draft PR #26. This protocol is frozen before the first full-corpus evaluation. Prior Rodinia traces were inspected, so these are **retrospective workloads, not prospective holdouts**. The producer hypothesis remains unverified.

## Source and unit of analysis
- Input: SHA-256 `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1` Purdue Accel-Sim 2020-03-18 Tesla V100 Rodinia archive, exactly 210 `.traceg` files. No external counters are assumed matched.
- Count **only** printed active `LDG` global-load rows, not `STG`, `ATOM`, `RED`, local/shared accesses, or zero-mask pseudo-rows. This is a SASS opcode proxy, not verified memory-path or actual DRAM read evidence.
- Use the historical 2020-03-09 tracer hypothesis `M=A&P`. For format 0, certify visible-lane addresses only if payload count equals `popcount(M)` (so `A=M`) or count is 32 (so `A=all lanes`). For format 1, certify visible addresses only when the lowest printed active lane is zero, or stride is zero; otherwise exclude. Reject unsupported format 2 rather than guessing. Any uint64 overflow fails closed. No fabricated addresses for excluded rows.
- Treat each `.traceg` file as an independent **address-identity domain**. Do not merge addresses across files or claim trace order is a GPU memory scheduling order. Never combine unknown addresses into the certified subset.

## Frozen descriptive quantities and analytic law
For each file f, over certified load instructions only, form a set of 128-byte aligned line IDs per instruction. Let R_f be the sum of their cardinalities and U_f the cardinality of their union. The exact order-independent *subset-only* reuse potential is D_f=R_f-U_f, fraction rho_f=D_f/R_f for R_f>0. In a hypothetical cold, fully associative, infinite-capacity, demand-only line-fill cache with no prefetch, fills equal U_f for this certified-only subsequence; with zero reuse, fills equal R_f. This is an elementary set identity, not novel GPU hardware or a physical throughput law.

A necessary condition for any **line-fill reduction** over that ideal infinite-capacity equal-resource baseline without changing referenced addresses is zero possible improvement: baseline already U_f. Any additional fixed-address coalescer is not a positive hardware candidate. The gap D_f is an upper bound on avoidable duplicate line requests **relative to a no-reuse model**, not an attainable GPU DRAM reduction. Because uncertified rows are omitted, R_f, U_f and rho_f are not whole-file estimates or valid full-file DRAM bounds.

Report per-application: total LDG rows, certified rows, excluded format-0/1 rows, certified coverage, R, U, D, rho; also number of files with no certified rows and the distribution of rho across files. Aggregate U by summing per-file unique counts, never by global address union.

## Frozen predicted regimes and checks
- Synthetic `hot_reuse`: 64 load instructions each touching four identical 128-byte lines. Predict R=256, U=4, D=252, rho=63/64.
- Synthetic `cold_stream`: 64 load instructions each touching four disjoint lines. Predict R=256, U=256, D=0, rho=0.
- An independent byte-enumeration oracle must reproduce line sets for widths 1, 4, 8, 16 and offsets 0, 31, 127; independent set accounting must reproduce synthetic regimes. Test hidden-lane format-0, shifted format-1, stride-zero format-1, uint64 overflow, malformed records, and file-domain separation.
- Full corpus must reproduce 210 trace files and previously observed 240,465 global-proxy rows (all LDG/STG/ATOM/RED), with all rows classified. Do **not** assume a specific observed rho or use Rodinia for unseen-validation claims.

## Kill/stop criteria
If the data are too ambiguously decoded to support a useful certified-only profile, report coverage and stop. Do not turn the elementary rho identity into a hardware invention. If the certified-only reuse potential is high, it still does not demonstrate GPU cache hit rate, DRAM traffic, occupancy, bandwidth, stalls, or performance. Advance hardware only after matched same-run traces/counters or validated cycle simulation, equal-resource RTL and electrical evidence. No RTX-5090 equivalence claims.
