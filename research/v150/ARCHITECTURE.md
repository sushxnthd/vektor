# V150 ARCHITECTURE ledger (2026-10-13)

**Changed block:** add a functional full-range binary32 RNE FMA reference for the V148 exact product/operand interface, including finite normals/subnormals, zeros, infinities, canonical NaNs and five IEEE flag bits (DZ remains zero for FMA).

**Why this changes the Vektor stack:** the reference defines the numerical contract for the future optimized general FMA finisher. It can detect cases V149 CLOSE-only cannot execute. It is deliberately 555-bit wide and should NEVER be deployed as the high-performance V-Tile datapath without independent PPA feasibility.

**Build gate:** V148 collector/multiplier and V149 CLOSE path previously passed CI; V150 full-range RTL functional gate is pending CI. Tagged architectural writeback and scoreboard are not yet integrated. No clock, area or power gate is passed for a full FMA.

**Required next:** integrate reference with Wave32 frontend; run full-Wave32 masks/tags/stalls, then implement a bounded/pipelined far/near design and compare to the exact reference and open FMA baseline. Synthesize both using the same flow, report actual timing/area rather than generic cell counts alone. Compare real KPX GEMM/reduction/vector/divergent kernels.

**Evidence classes:** software oracle VERIFIED locally on 16,916 cases, 14,887 finite cases cross-checked against libc; HDL RTL PENDING; physical PPA NOT MEASURED; GPU throughput NOT MEASURED. RTX 5090-class: INCONCLUSIVE. Spend: $0.
