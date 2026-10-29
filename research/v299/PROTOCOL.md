# V299 prospective synthetic falsification protocol (2026-10-29)

## Candidate and physical meaning

**One candidate:** age-decayed fanout-weighted translation retention in an eight-entry, fully associative synthetic GPU TLB. A warp translation miss can stall multiple same-page consumers; retain recently reused translations with large measured waiting-warp fanout, but decay their priority as their reuse phase ends. Per-entry fields: last-use age, 2-bit saturating frequency, 2-bit fanout bin. Victim score is `(frequency * fanout_bin) >> min(4, age // 16)`, with oldest-first tie breaking. The score is an integer shift, not an exponential circuit. It is not yet RTL, not a claim of novel cache replacement, and not a reproduction of DEPOT.

## Predeclared controls

All five policies receive identical request streams and have eight entries (32 in ample capacity). `lru`, 2-bit `lfu`, binary `fanout_lru`, and 2-bit `fanout_lfu` are the controls. All policies are simulated with the same metadata visibility, though they have **not** been proven equal in mapped area or timing. The strongest control is selected per regime, not just LRU.

## Pilot isolation and frozen evaluation

Exploratory seeds **11, 17, 23, 31** were used to choose the integer score and 16-cycle age bucket. They are **not** prospective. Holdout seeds **503, 509, 521, 523**, 20,000 references/seed, seven regimes, and fixed 100-cycle miss penalty are frozen **before** running the holdout. No parameter tuning after opening holdouts. This experiment is synthetic only; no trace claims.

Predicted-win regime: `phase` (hot high-fanout translation set rotates every 3,000 accesses), with >=3% lower mean `stall_work` than the strongest control. Predicted-no-win regime: `uniform` (all fanouts one), with absolute advantage <=1%. Robustness kill: if V299 increases `stall_work` by >5% over the strongest control on **any** of `skew`, `scan`, `reverse`, `burst`, or `ample`, retire immediately. Passing the two predictions alone is insufficient. Do not promote V299 unless all gates pass and physical timing/area and genuine GPU traces subsequently support it.

`stall_work = sum(miss_fanout * 100)` is a **non-overlapped warp-cycle proxy**. It is not elapsed time, IPC, cache hierarchy throughput, page-walk concurrency, or RTX 5090 performance. No physical RTL exists. A false-positive fanout on a streaming page can cause pollution, which `reverse` tests explicitly.

## Prior-art boundary

DEPOT (Anik et al., arXiv:2606.00486, May 2026) explicitly addresses dead-entry GPU TLB misses and distinguishes burst amplification from capacity overflow. MeDiC (Ausavarungnirun et al., arXiv:1804.11038) addresses GPU memory divergence. Cost/frequency/recency-aware cache replacement is established. The proposed weighted score is **not** a demonstrated novel principle. Sources: https://arxiv.org/abs/2606.00486 and https://arxiv.org/abs/1804.11038.

## Reproduce

`python3 research/v299/v299_tlb_fanout.py --selftest --evaluate`. The report must preserve all controls, failures and per-seed results. Independent verification and PPA remain required before any positive architectural claim.
