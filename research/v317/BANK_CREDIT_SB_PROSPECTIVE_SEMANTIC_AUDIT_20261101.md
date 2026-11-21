# V317 bank-credit S/B scaling: independent semantic audit and hosted physicality gate (2026-11-01)

## Source and evidence tier
The prospective protocol was committed first at `b2d669fb`, before parameterized RTL, testbench, checker, parser or workflow. This report records only what was actually executed locally and what is still pending. The complete source-pinned [hosted nine-point run #41288324467](https://github.com/sushxnthd/vektor/actions/runs/41288324467) was **queued** at inspection; do not treat the intended RTL or synthesis steps as passed.

## Independent algorithmic validation
The reproducible `python -m research.v317.rtl.check_rf_sb_scaling` implementation was independently executed locally. It passed **1,024 exhaustive** S=2,B=4 configurations (all 4 request-valid masks times all 4^4 operand combinations), plus **2,048 deterministic random** configurations for each of nine S/B combinations, for **19,456 software semantic comparisons** with zero discrepancies. The oracle uses a per-bank integer read counter. The bank-mask model tracks first/second occupancy, while the pairwise model counts previously granted operand matches. This is **software algorithmic validation**, not an executed Verilog test or formal proof of the new RTL.

## Equivalence invariant and zero-service consequence
For each bank b after processing slots 0..i-1, let C_i(b) count physical operands of previously granted requests. The bank-mask state satisfies `once_used[b] == (C_i(b)>=1)` and `twice_used[b] == (C_i(b)>=2)`. The pairwise test computes the same counts by matching all previously granted operands. Initially all are zero. A same-bank request (b,b) can be granted iff C_i(b)=0; a distinct-bank request (a,b) can be granted iff C_i(a)<2 and C_i(b)<2. Both updates add the same two operands, preserving the invariant by induction. Therefore both **algorithmic policies** grant identically for any S,B and valid bank IDs. A Verilog implementation bug can still violate this theorem, hence independent RTL simulation is mandatory.

**Physical and performance boundary:** identical grants imply exactly zero intrinsic incremental completed-service or register-bank-traffic benefit at matched clock, port budget and workload. A generic-cell reduction could reduce implementation cost, but is not a new GPU scheduling mechanism or a demonstrated throughput win.

## Frozen scaling test awaiting hosted evidence
The nine pairs are S={2,4,8} x B={4,16,64}. Both RTL designs use the same Yosys `synth -flatten; stat; ltp -noff; write_json` sequence. The [workflow](../../.github/workflows/v317-rf-sb-scaling.yml) will preserve independent software and RTL logs, full generic netlists, fanout, flip-flops, cell counts, logic depth, exact source SHA, and failed results.

The frozen hypotheses are: pairwise has fewer generic cells at S=4,B=16; at fixed S=4 its relative cost ratio does not increase with B; at S=8,B=4 a crossover to pairwise being more costly may occur. **No measured nine-point synthesis values exist in this report**; none of these predictions is scored as survived or falsified yet.

## Research decision
Retain pairwise bank credit solely as a lower-cost, source-equivalent implementation baseline pending the hosted sweep. V317 forwarding and exact-cardinality scheduling remain rejected. Neither standard-cell mapped timing, routed electrical checks, real register-bank workload traces, power, nor integrated tile area is established. Do not claim GPU IPC gain, novel scheduling, or RTX 5090 equivalence. Kernellum PR #119 was inspected read-only and not modified.


## Hosted nine-point result (subsequent source-pinned update)
[GitHub Actions run #41288324467](https://github.com/sushxnthd/vektor/actions/runs/41288324467) at `0d3933bfaee8e511d3b6282c8afd3ab9fca08c93` **passed** all steps: independent software checker, nine RTL oracle configurations, nine matched bank-mask/pairwise generic synthesis pairs, cost parser and evidence upload ([artifact #13076271732](https://github.com/sushxnthd/vektor/actions/runs/41288324467/artifacts/13076271732)). The Verilog oracle ran **19,474** directed, exhaustive and seeded cases across nine configurations (9*2,050 + 1,024). All passed.

| Slots S | Banks B | Bank-mask cells | Pairwise cells | Pairwise/mask | Mask levels | Pairwise levels |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 4 | 47 | 24 | 0.5106 | 9 | 7 |
| 2 | 16 | 260 | 44 | 0.1692 | 16 | 8 |
| 2 | 64 | 957 | 64 | 0.0669 | 21 | 9 |
| 4 | 4 | 297 | 158 | 0.5320 | 47 | 15 |
| 4 | 16 | 1,353 | 266 | 0.1966 | 71 | 16 |
| 4 | 64 | 5,179 | 374 | 0.0722 | 92 | 17 |
| 8 | 4 | 797 | 762 | 0.9561 | 123 | 31 |
| 8 | 16 | 3,535 | 1,238 | 0.3502 | 179 | 32 |
| 8 | 64 | 13,621 | 1,714 | 0.1258 | 232 | 33 |

**Frozen prediction scoring:** P1 passed in hosted RTL simulation; P2 (S=4,B=16 pairwise fewer cells and monotonically improving relative ratio with B) passed; P3 (S=8,B=4 pairwise crossover to more cells) **falsified**: pairwise was 762 vs 797, a 4.39% saving. P4 identical service follows the proven algorithmic invariant and the sampled RTL oracle, not real GPU workload measurements. P5 physical signoff remains unmet.

**Important scope:** This is a newly parameterized bank-mask RTL comparator, not exactly the old fixed-priority RTL (at S=4,B=16 the old source measured 1,321 generic cells, this bank-mask comparator 1,353). Both new implementations use identical inputs, slots and bank ports, but no mapped area/clock claim follows. The new pairwise RTL has not yet received a complete all-input SAT equivalence proof at every parameter point; the existing fixed S=4,B=16 pairwise module has a separate earlier full proof.

**Observed scaling hypothesis for a prospective holdout:** At S={2,4,8}, pairwise cells increase linearly with W=log2(B): per added bank-index bit, +10, +54, +238 cells respectively. Those three slopes fit `4*S*S - 2*S - 2`; the W=2 intercepts fit `14*S*S - 17*S + 2`. The compact **descriptive** synthesis law is therefore `C_pair(S,W)=(14*S*S-17*S+2)+(4*S*S-2*S-2)*(W-2)`. It is not yet a validated predictive law for unseen S or W and is not a physical area model. Prospective holdouts must be frozen and tested separately.
