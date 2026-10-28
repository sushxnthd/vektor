# V297 prior-art kill audit, first pass (2026-10-29)

This is a first-pass literature audit, not an exhaustive novelty or patent search. The presence of a similar objective is not proof of identical circuitry; no novelty claim should be made until the exact selection logic is compared.

1. **Yamada et al., "Bank-Aware Instruction Scheduler for a Multibanked Register File" (2018)**, DOI [10.2197/ipsjjip.26.696](https://doi.org/10.2197/ipsjjip.26.696), [journal page](https://www.jstage.jst.go.jp/article/ipsjjip/26/0/26_696/_article). Directly relevant: selects simultaneously issuable instructions to avoid register-file bank conflicts; the paper also treats scheduler latency and circuit area. **Closest discovered architectural precedent** for V297's compatible-pair selection, although it targets superscalar CPUs rather than GPU warp issue.
2. **Gou & Gaydadjiev, "Addressing GPU On-Chip Shared Memory Bank Conflicts Using Elastic Pipeline" (2013)**, DOI [10.1007/s10766-012-0201-1](https://doi.org/10.1007/s10766-012-0201-1). GPU bank-conflict-aware warp scheduling and elastic pipeline; targets shared-memory conflicts and writeback stalls, not exactly the proposed register-file read-port selector.
3. **Jog et al., "Orchestrated Scheduling and Prefetching for GPGPUs" (ISCA 2013)**, DOI [10.1145/2485922.2485951](https://doi.org/10.1145/2485922.2485951). Warp scheduling changes bank-level parallelism and memory latency; warns against comparing only to naïve round robin.
4. **Shoushtary et al., "A Lightweight, Compiler-Assisted Register File Cache for GPGPU" (2023)**, [arXiv:2310.17501](https://arxiv.org/abs/2310.17501). RF bank conflicts, RF caching, and dynamically adapted issue scheduling; register-file architecture and energy are already co-optimized.
5. **"Enabling High-Capacity, Latency-Tolerant, and Highly-Concurrent GPU Register Files via Software/Hardware Cooperation" (2020)**, [arXiv:2010.09330](https://arxiv.org/abs/2010.09330). Compiler register renumbering reduces RF bank conflicts; strong software/hardware alternative.

## Implication
V297's maximum-feasible-pair effect and finite cooldown are **not established novel**. The queue experiment nearly matches an exhaustive maximum-cardinality oracle, which is consistent with an ordinary small-set scheduling improvement. A credible novel claim would require a non-obvious physical/temporal boundary that beats an implemented, timing/area-matched bank-aware scheduler, not merely fixed or rotating serial priority. No RTX-5090-level claim.

## Next audit tasks
Read Yamada et al. select logic and hardware evaluation in full; compare their bank-feasible scheduling objective and priority/fairness to V297 line by line. Add patent search and later GPU-specific operand collector literature. Do not equate shared-memory conflicts with register-file read-port conflicts.
