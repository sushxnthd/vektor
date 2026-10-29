# V307 no-go: mapped Nangate45 falsifies next-bank-pressure tie-break (2026-10-29)

**Decision: RETIRE V307.** This is a falsification of the frozen candidate and its current unoptimized registered RTL, not a proof that all bank-pressure heuristics are impossible. Do not open holdout seeds 2001–2020. Preserve this branch and close draft PR #24 unmerged.

## Evidence and provenance

First hosted run: [40899864912](https://github.com/sushxnthd/vektor/actions/runs/40899864912), [raw artifact 12908478002](https://github.com/sushxnthd/vektor/actions/runs/40899864912/artifacts/12908478002). Exact common synthesis conditions: Yosys 0.33, one registered RTL module `v307_issue_select`, MODE=0 MAX-NOW, MODE=1 PRESSURE, MODE=2 exact FUTURE-TIE, same I/O, pinned Nangate45 typical Liberty from OpenROAD-flow-scripts revision `eda8e552974d47a12616294dddf4012d892548d3`, ABC nominal load 10 fF and target 10,000 ps. The target is a **mapping constraint, not measured timing**. All seven individual Yosys runs exited zero with structural check passing; clocked 256-vector independent oracle passed all modes.

| Mode | Nominal mapped standard-cell area (um^2) |
| --- | ---: |
| MAX-NOW, MODE=0 | 380.380 |
| V307 PRESSURE, MODE=1 | **9,454.704** |
| FUTURE-TIE, MODE=2 | **2,608.662** |

V307 is **24.8559x** the MAX-NOW mapped cell area and **3.62435x** the strongest same-information FUTURE-TIE control. The prospective pilot already showed V307 at **-0.3882% mean per-seed synthetic throughput gain** versus FUTURE-TIE on W1, with a -6.5421% individual-seed tail. The physical screen was committed before mapping: nominal V307 area must be at most 90% of FUTURE-TIE and at most 120% of MAX-NOW. **Both conditions fail by large margins.** No unseen workload evaluation is justified.

## Output-load sensitivity and reporting failure

| ABC output load | MAX-NOW (um^2) | V307 PRESSURE (um^2) |
| --- | ---: | ---: |
| 2 fF | 380.380 | 9,454.704 |
| 10 fF | 380.380 | 9,454.704 |
| 30 fF | 384.370 | 9,458.694 |

The strongest FUTURE-TIE was **not** mapped at 2 or 30 fF. No FUTURE-TIE load-corner comparison is claimed. The first hosted workflow reported failure because the summary script accessed an absent `mode2_load2ff` result *after all seven synthesis cases succeeded*. The raw mapping logs were uploaded, and the script was repaired to fail closed when optional control corners are absent (commits `0c2f2a8`, `b9ea31b`). A successful rerun is required for a machine-generated JSON summary, but is **not** needed to establish the already-opened nominal-area falsification.

## Mechanistic and external-validity limits

- The model assumes five warps sharing an eight-bank domain, three issue slots, and atomic two-distinct-bank operand reads. It excludes real operand-collector queues, staggered operand reads, same-bank operands, scoreboard dependencies, physical placement and wire delay.
- Barnes, Shen and Rogers, *Mitigating GPU Core Partitioning Performance Effects*, HPCA 2023 (https://engineering.purdue.edu/tgrogers/publication/barnes-hpca-2023/barnes-hpca-2023.pdf), report two register-file banks per sub-core for Volta V100 and Ampere A100, with partitioned collectors. Under V307's **own** atomic two-bank-read assumption, two banks permit at most one issue/cycle; all tie-break policies are equivalent. This is an exact no-win boundary for that model, not a verified Blackwell/RTX 5090 specification.
- Bank-aware scheduling is prior art (Barnes et al. 2023). Related operand-collector research includes Triple-A (IEEE Embedded Systems Letters 2024, DOI 10.1109/LES.2023.3307622) and Memento (ISCA 2024, DOI 10.1109/ISCA59077.2024.00075). Pressure-aware warp scheduling also appears in RPAWS (2026, https://globals.ieice.org/en_publications/elex/10.1587/elex.23.20260028/_f), although it targets execution-unit rather than RF-bank pressure. No broad novelty claim survives.

## Honest scope

These are **mapped standard-cell area proxies**, not placed/routed area, timing closure, DRC, extracted RC, energy, whole-SM performance, GPU IPC or RTX-5090 equivalence. The RTL uses exhaustive subset enumeration and integer pressure counters; an optimized implementation might be smaller. However, the frozen candidate does not outperform the strongest synthetic control and its current implementation is much larger. Retuning the opened pilot or relabeling the unoptimized implementation as a success would be scientifically invalid.

**Next Vektor research must first reproduce a real workload bottleneck with realistic sub-core RF/collector organization and strong literature baselines. Do not promote another speculative scheduling policy solely on synthetic throughput.**
