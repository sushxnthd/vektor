# V309 external-PTX workload audit: negative qualification result

Date: 2026-10-29. **Evidence tier: static compiler-produced PTX, not SASS or dynamic execution.**
Frozen protocol: `PROTOCOL.md` committed at `cee79d1e5199a81621586754531f5843f377f38a` before parser implementation and hosted measurements. Both external source files had been inspected before freeze, so these are **not prospective unseen holdouts**.

## Reproduced external-source results
[Hosted evidence run #40919429622](https://github.com/sushxnthd/vektor/actions/runs/40919429622) passed at `0f252752`; artifact ID `12916109235` includes JSON, with upstream Git blob identities checked before parsing. A later hardened-parser run [#40919622410](https://github.com/sushxnthd/vektor/actions/runs/40919622410) also passed. The final [independent-audit CI #40919712774](https://github.com/sushxnthd/vektor/actions/runs/40919712774) **passed** at `5e231e08`, including four independent JSON mutations and the parser's four malformed-input mutants.

| Static metric | Stanford CS336 Triton GELU | parallel101 atomic reduction |
|---|---:|---:|
| Compiler PTX target | sm_100a | sm_52 |
| Static instructions in one entry | 134 | 23 |
| Explicit data-register source occurrences | 181 | 21 |
| Unique data sources within each instruction (summed) | 173 | 21 |
| Duplicate occurrences removable by free within-instruction broadcast | 8 | 0 |
| Duplicate fraction of naive source occurrences | 4.4199% | 0% |
| Mean unique data sources per static instruction | 1.291045 | 0.913043 |
| Static memory instructions | 7 | 5 |
| Predicated instructions | 4 | 2 |
| Conditional 2-bank, 1-read-port aggregate service cycles | 87 | 11 |
| Conditional 4-bank, 1-read-port aggregate service cycles | 44 | 6 |
| Conditional 8-bank, 1-read-port aggregate service cycles | 22 | 3 |

**Independent audit:** `audit_results.py` checks source blob IDs, exact source counts, opcode conservation, read conservation, lower-bound arithmetic and mutation detection without importing the parser. The parser separately has destination/source and vector/predicate fixtures and four malformed-input mutants. The hosted independent audit is verified green at run #40919712774.

## Hard scientific boundary
Under the hypothetical scalar PTX operand-demand model, the absolute opportunity from eliminating duplicate reads within a single instruction is only 8/181 = **4.4199% of naive GELU reads**, and **0% for atomic reduction**. The corresponding naive/unique read-demand ratio is 181/173 = **1.04624x** for GELU. This is not an architectural speedup: the strongest baseline already broadcasts identical within-instruction sources, and source registers are virtual PTX registers.

The aggregate service-cycle formula `ceil(U/(B*P))` is a **conditional arithmetic proxy** for a fictitious machine that executes every PTX operation and fetches every counted virtual operand from an RF. Real SASS lowering, register allocation, operand bypass, dependencies, branch frequencies, caches, bank mapping, occupancy, and physical wiring are unknown. Consequently these numbers **cannot be interpreted as measured GPU bank pressure or even unconditional lower bounds on actual hardware cycles**.

## Decision
**No V309 architecture mechanism is promoted.** The external-PTX audit does not establish a physical bottleneck or a positive predictive hardware law. Reject any duplicate-source-broadcast-only novelty/performance claim; it offers no advantage over the strong broadcast control. Do not spend RTL/physical-routing effort on it.

The next qualification must acquire >=3 independent workload families with actual SASS/dynamic instruction traces or measured performance counters, plus an independently validated PTX-to-SASS mapping, and freeze predicted-win/no-win regimes before selecting a single new mechanism. Do not recycle V287/V296/V303/V307/V308 without a new measured bottleneck.

Kernellum PR #119 and its prospective holdouts remain untouched. No routed GPU area, timing, electrical, power, IPC, or RTX-5090-equivalence claim.

## Next evidence acquisition route (not yet executed)
[Accel-Sim 2.0](https://github.com/accel-sim/accel-sim-framework) documents publicly released pre-collected **real SASS traces with paired Nsight Compute statistics**. Its release index lists H200 workloads (including BERT, ResNet, Llama, SDXL and others) and SHA-256 checked per-configuration downloads. Each configuration is approximately 1–50 GB, so the next run must first identify the **smallest** no-cost eligible sample and verify storage/CI budgets; do not download hundreds of GB or claim a completed hardware trace. The framework's current Blackwell support is roadmap/experimental, not proof of RTX 5090 validation.

Pre-register an external three-family holdout before using any such traces for architecture selection. Extract dynamic SASS operand mix, instruction dependency distance, bank conflict/collector stalls where observable, and measured counter correlations. Require a quantified bottleneck and a same-information baseline before naming V310.
