# V308 prospective no-go: two-bank collector completion-first arbitration (2026-10-29)

**Decision: RETIRE V308.** This is a synthetic falsification, not a real GPU workload bottleneck reproduction. Frozen protocol committed at `1a3369d2822a38946a3944d785ec156839c3e26b` before opening seeds 1001–1008. The opened pilot used only seeds 31–34. No retuning or threshold change was made.

## Matched resource and control
Each instruction needs two source RF reads, potentially to the same bank. Both banks have one read port; four collector slots are shared; admission is at most one instruction per cycle; reads may be staggered. The candidate COMPLETION chooses legal bank grants maximizing instructions finished that cycle. Strong simple SRPT chooses grants favoring instructions with fewer remaining reads. OLDEST is a weaker control. All three see identical 1,200-instruction traces and resources.

## Prospective W1: IID source banks

| Seed | OLDEST cycles | SRPT cycles | COMPLETION cycles | Candidate vs SRPT throughput |
|---|---:|---:|---:|---:|
| 1001 | 1310 | 1283 | 1278 | +0.3912% |
| 1002 | 1322 | 1300 | 1297 | +0.2313% |
| 1003 | 1330 | 1307 | 1306 | +0.0766% |
| 1004 | 1320 | 1302 | 1299 | +0.2309% |
| 1005 | 1329 | 1302 | 1297 | +0.3855% |
| 1006 | 1324 | 1296 | 1292 | +0.3096% |
| 1007 | 1336 | 1308 | 1302 | +0.4608% |
| 1008 | 1326 | 1293 | 1289 | +0.3103% |

Mean of per-seed throughput gains vs SRPT: **+0.299538%**. Versus OLDEST: **+2.288945%**. The preregistered gate was **at least +5% vs SRPT**. The candidate fails decisively. These are synthetic completed instructions per cycle, not GPU IPC.

## Frozen N1 and sensitivity regimes

| Regime | Mean COMPLETION gain vs SRPT | Mean vs OLDEST | Finding |
|---|---:|---:|---|
| ALL_CROSS (N1) | 0.000000% | 0.000000% | Exactly predicted no-win |
| SKEW | 0.000000% | 0.000000% | All policies reach dominant-bank bound |
| ALTERNATING | 0.000000% | 0.000000% | All policies tied |
| MIXED | 0.000000% | 0.000000% | All policies tied |
| IID (W1) | +0.299538% | +2.288945% | Below 5% gate |

SKEW: for seeds 1001–1008, all three policies finish in **2055, 2057, 2043, 2033, 2030, 2034, 2056, 2040** cycles respectively. ALL_CROSS: all three finish in exactly **1200** cycles for every seed. ALTERNATING: 1374 cycles for every seed and policy. MIXED: 1201 cycles for every seed and policy. All raw per-seed outcomes are reproducible from `collector.py` without hidden inputs.

## Predictive boundary and audit

For N instructions and D_b source reads demanded from each bank b, a one-port-per-bank execution requires `C >= max_b D_b` and `C >= N` (two reads/instruction, two banks). Thus `T <= min(1, N/max_b D_b)`. This is a **necessary upper bound**, not a tight general throughput law or a new mechanism. In SKEW, the dominant-bank lower bound is met exactly; arbitration cannot improve makespan within this fixed model. In ALL_CROSS, each bank has N reads, so the one-instruction-per-cycle throughput ceiling is attained.

The independent demand checker recomputes bank demand directly from every trace and verifies each policy's read accounting, completed count, port lower bounds, collector capacity, mean performance and the no-go gate: **781 assertions** over 40 unseen traces × 3 policies. The separate exhaustive selector test checks 2,340 small states, with 45 conservation/capacity replays and a low-load no-win test. All local tests passed. No hosted CI or independent third-party reproduction is claimed until it completes.

## Limits, prior art, and disposition

This is not a benchmark trace from a real GPU. The model omits scoreboard dependencies, execution pipelines, cache, bypass, writeback, clocking, area, energy, wires and physical timing. Two banks are an illustrative Volta/Ampere-like independent scheduler domain, not a measured RTX 5090 bank topology. Bank-aware scheduling and operand collectors are established prior art (Barnes et al., HPCA 2023: https://engineering.purdue.edu/tgrogers/publication/barnes-hpca-2023/barnes-hpca-2023.pdf).

**Kill V308 without RTL or physical investment.** Its ~0.3% mean win over SRPT cannot justify new scheduler hardware. Do not promote another synthetic bank-scheduling candidate until an external workload trace or independently validated bottleneck is available. Preserve all negative evidence, and do not reopen V287, V296 or V307 merely by relabeling their mechanism.

Reproduce from repository root:
```bash
cd research/v308
python3 -m unittest -v test_collector.py
python3 collector.py --pilot
python3 collector.py > holdout.json
python3 audit.py
```

No GPU throughput, routed timing, power, or RTX-5090-equivalence claim.
