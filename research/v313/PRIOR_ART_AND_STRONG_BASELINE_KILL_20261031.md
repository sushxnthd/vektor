# V313: prospective synthetic win, decisive prior-art/strong-control kill (2026-10-31)

**Decision: RETIRE V313 as a novel GPU architecture mechanism.** Do not implement RTL or spend routing budget on this candidate. This is a scientific negative result, not a failed CI or a claim that early operand collection is ineffective.

## Source-pinned heldout results
The frozen [protocol](SLACK_ONLY_EARLY_OPERAND_PREREG_20261031.md) was committed as `585d6062` before the heldout script and seeds were run. The hosted [prospective run #41187467810](https://github.com/sushxnthd/vektor/actions/runs/41187467810) passed on commit `3cb8c353`. The model is a synthetic 4-slot/16-bank/2-port/FIFO service simulator, NOT a GPU performance model.

| Frozen regime | Ready-only completed | Slack-only early completed | Ratio | Early RF reads | Dropped baseline/candidate |
|---|---:|---:|---:|---:|---:|
| Win, seed 313701 | 45,334 | 46,816 | **1.0326907x** | 6,745 | 26,615 / 25,133 |
| No-win, seed 313702 | 71,798 | 71,798 | **1.0000000x** | 0 | 83 / 83 |
| Perturbed transfer, seed 313703 | 51,897 | 53,297 | **1.0269765x** | 7,553 | 20,169 / 18,768 |

Win prediction 1.02–1.06 and no-win exact equality both passed. The win p99 synthetic latency changed 11 -> 10 cycles; transfer 10 -> 9. These are model cycles only. Neither physical RF traffic nor dynamic energy has been measured. The simulator excludes dependencies across queued instructions, finite collector allocation outside per-slot FIFO, full register version tracking, forwarding, scoreboard implementation, power, and actual kernel traces.

## Decisive novelty failure
**Triple-A: Early Operand Collector Allocation for Maximizing GPU Register Bank Utilization**, Ipoom Jeong, Eunbi Jeong, Nam Sung Kim and Myung Kuk Yoon, IEEE Embedded Systems Letters 16(2), 206–209 (2024), DOI: https://doi.org/10.1109/LES.2023.3307622, explicitly allocates an operand collector before all source operands are ready and includes forwarding, RF write bypass and latency-aware allocation. Its published reported performance and energy changes are not reproduced here. Primary author page: https://ipoom-jeong.com/publication/triple-a-early-operand-collector-allocation-for-maximizing-gpu-register-bank-utilization/

V313's *central architecture action* (collect a ready operand while another remains blocked) is therefore established prior art. Restricting the read to otherwise idle bank ports is a conservative scheduling policy, not evidence of a new hardware principle. An equal-information early-capable buffered collector can implement precisely the same policy and admit precisely the same work; a ready-only baseline is too weak to support novelty. The independent [same-information checker](strong_early_collector.py) uses a separately coded bank-budget scheduler and checks all three frozen streams. **This is a policy-equivalence construction, not a faithful RTL reproduction of Triple-A or a claim about its exact performance.**

## Safety and physical gates
Early collection is legal only with a correct register-version / WAR / RAW invariant or verified replay; no such proof is provided. The initial prefilter is useful for understanding temporal bank slack, but its gain cannot be called a new architecture result. No RTL, synthesis, area, clock, slew, capacitance, placed RC, routed parasitics, workload throughput, or power evidence was generated for V313.

## Research decision
Retire V313 without promoting it into physical design. Preserve both its prospective synthetic positive result and the independent strong-control/novelty failure. Future candidates must beat a Triple-A-class early-collector baseline and show an **incremental** mechanism, not simply reproduce pre-issue operand collection. V312 remains physically rejected in draft PR #29. V287 and V296 are historical; do not reactivate them.
