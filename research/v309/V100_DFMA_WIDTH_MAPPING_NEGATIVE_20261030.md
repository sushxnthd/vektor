# V309 DFMA width and mapping sensitivity: RETIRE (2026-10-30)

**Decision:** DFMA-only register-bank-conflict hardware is **retired for the examined V100 Rodinia corpus** under the preregistered 1% conditional isolated-service proxy. No GPU architecture mechanism promoted. The threshold was frozen in [DFMA_WIDTH_MAPPING_PROTOCOL_20261030.md](DFMA_WIDTH_MAPPING_PROTOCOL_20261030.md) at commit `ec3a697`, before the new full-corpus evaluation.

## Authentication and reproducibility

- Source: original Purdue 2020 Tesla V100 Rodinia SASS archive, SHA-256 `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1` (21,011,152 compressed bytes). [Original source](https://engineering.purdue.edu/tgrogers/accel-sim/traces/tesla-v100/2020.03.18/rodinia_2.0-ft.tgz).
- [Hosted GitHub Actions #40969927219](https://github.com/sushxnthd/vektor/actions/runs/40969927219): **all steps passed**, including independent full-archive redecoder, SHA verification, both selftests, 21 adversarial report mutants, and raw artifact upload.
- [Raw primary and independent audit artifact #12939846839](https://github.com/sushxnthd/vektor/actions/runs/40969927219/artifacts/12939846839).
- [Primary profiler](dfma_width_envelope.py) and [independent redecoder](audit_dfma_width_envelope.py). The independent checker does not import the primary parser or accounting functions.

## Exact conditional workload results

The model deduplicates identical source tokens, assumes R255 bypass, and compares hypothetical two-bank mapping rules for each 64-bit DFMA source: PAIR bank = floor(R/2) mod 2, RAW bank = R mod 2. P is the assumed number of 64-bit operand reads/bank/isolated service cycle.

| Metric | Result |
|---|---:|
| Active dynamic SASS instruction rows | 3,937,565 |
| DFMA rows | 43,949 (1.1161% of all active rows) |
| DFMA rows containing an odd-index non-R255 source base | **0** |
| PAIR mapping, P=1, conditional extra slots | **36,779 (0.93405% of all rows)** |
| PAIR mapping, P=2, conditional extra slots | **0** |
| RAW mapping, P=1, conditional extra slots | 79,704 (2.02420% of all rows) |
| RAW mapping, P=2, conditional extra slots | 36,779 |
| Rows whose PAIR and RAW P=1 service differ | **42,925 (97.67% of DFMA rows)** |
| Rows whose PAIR and RAW P=2 service differ | 36,779 |

Per-application PAIR/P1 extra slots: Hotspot 31,659; Backprop 4,096; SRAD-v2 1,024; eight other families zero. This concentration was discovered in already examined workloads and is **not prospective validation**.

The frozen PAIR/P1 threshold was 1% of all active rows. The observed 0.93405% falls below it. Therefore **RETIRE_DFMA_ONLY**, even before considering latency hiding, bank arbitration, control area or timing. Do not lower the threshold after inspection.

## Crucial physical interpretation

Jia et al. (2018), [Dissecting the NVIDIA Volta GPU Architecture via Microbenchmarking](https://arxiv.org/abs/1804.06826), report two 64-bit-wide banks and a register-index-modulo-two mapping for 32-bit register operands, with FFMA conflicts for three same-bank sources. They do **not** establish that a 64-bit DFMA source pair can be treated as one 64-bit operand resident entirely in bank floor(R/2) mod 2.

Indeed, all 43,949 traced DFMA rows have **even** source-base indices (excluding R255). If each 64-bit DFMA operand uses a consecutive even/odd register pair, its two 32-bit halves would occupy opposite modulo-two banks. Under that plausible split-pair model, every distinct DFMA source consumes 32 bits in **both** banks; bank assignment is then invariant to register-pair renaming. With 64-bit per-bank service, two distinct 64-bit sources can be served per cycle, and three require two isolated service cycles. **Such fixed width demand is not a bank-conflict-remapping opportunity.** This is a conditional architectural deduction, not measured silicon behavior. Compiler register reuse, operand caching, collector scheduling and bypass could change actual service.

The RAW mapping places every even base on bank zero, which is inappropriate as a literal 64-bit-pair bank assignment. Its large conditional extras illustrate how a mistaken source-token mapping creates spurious hardware opportunities. PAIR is also a sensitivity model, not validated silicon behavior. Neither should be interpreted as measured stalls.

## Negative result and next gate

The prior all-opcode P=2 residual of 39,413 idealized extra slots included 36,779 DFMA slots. This experiment shows why transferring 32-bit FFMA bank assumptions to 64-bit DFMA is invalid. Even the optimistic PAIR/P1 proxy fails the frozen 1% gate; the physically plausible split-pair interpretation makes register remapping unable to eliminate intrinsic width service in isolation.

**Not established:** actual V100 bank conflicts, counter-attributed stall cycles, collector organization, matched GPU IPC, RTL/area/timing/power, Blackwell bank mapping, or RTX 5090 performance. No genuine unseen workload-family transfer has been performed.

**Next:** stop proposing bank-remapping hardware from this corpus. Acquire matched hardware counters or validated cycle simulation on a new workload family; freeze win/no-win predictions before any new architecture mechanism. Existing draft PR #26 remains a qualification/evidence PR; retired V287/V296/V297–V308 stay retired. Kernellum PR #119 remains unchanged.
