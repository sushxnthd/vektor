# V309 DFMA width and bank-map identifiability protocol (frozen before analysis)

Date: 2026-10-30. This is a **qualification/falsification** experiment on previously examined V100 Rodinia families, **not** an unopened holdout. No hardware mechanism is active or promoted.

## Fixed provenance
Purdue Accel-Sim Tesla V100 Rodinia SASS trace archive:
https://engineering.purdue.edu/tgrogers/accel-sim/traces/tesla-v100/2020.03.18/rodinia_2.0-ft.tgz
SHA-256 `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`.
Previously observed 3,937,565 active rows, 11 application families, and 36,779 of 39,413 idealized P=2 all-opcode extras attributed to DFMA. Those are **known observations**, not new predictions.

## Physical question and competing models
FFMA's 32-bit bank-service interpretation must not be applied to DFMA's 64-bit operands. Treat distinct DFMA source register tokens as possible 64-bit operands, *hypothetically* encoded by consecutive 32-bit register pairs. Test both:
- PAIR: two 64-bit banks; bank = floor(R/2) mod 2.
- RAW: two banks; bank = R mod 2. This is a counterfactual mapping sensitivity, not a verified DFMA mapping.
- For each, P=1 and P=2 **64-bit operand reads per bank per isolated instruction-service cycle**.
- Deduplicate repeated source tokens for a strongest free-broadcast baseline; provisionally bypass R255, with a no-bypass PAIR/P1 sensitivity.
- Record DFMA source bases with odd register indices. If prevalent, the simple register-pair interpretation is questionable.
- Exclude zero-mask rows. Do not assume collector arbitration, co-issue, bypass timing, scoreboard effects or latency hiding.

For source set S, mapping m and port count P, define conditional extra service slots
`E_m,P(S) = max(0, ceil(max_b |{r in unique(S)\{255}:m(r)=b}| / P) - 1)`.
Aggregate E across dynamic DFMA rows; report E/N as a *conditional isolated-service proxy*, never GPU stalls or actual throughput headroom.

## Frozen decision
If PAIR/P1 E/N < 1%, **retire DFMA-only bank-conflict hardware** for this corpus. If >=1%, do **not** promote hardware: require paired V100 counters/validated simulation, credible operand-pair semantics, collector model and matched-resource RTL timing/area. Strong mapping disagreement or odd-source prevalence triggers **mapping-unidentified** irrespective of proxy size. Report all outcomes, including negative and contradictory ones. Do not retrofit threshold after inspection.

The existing 11 Rodinia families are already explored; no prospective workload transfer can be claimed. Before architecture selection, acquire an **independent external workload family** and freeze predicted-win and predicted-no-win regimes with source hashes. Prior work: Jia et al. (2018) https://arxiv.org/abs/1804.06826; do not extrapolate published FFMA bank behavior to DFMA without validation.

## Reproducibility and integrity
New standalone primary profiler plus independent parser/auditor; SHA-pinned archive; CI must reject mutated counts and provenance, and retain raw JSON. Never report this as RTX 5090 data, power, area, timing or GPU IPC.