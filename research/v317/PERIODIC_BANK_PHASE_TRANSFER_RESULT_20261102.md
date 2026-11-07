# V317 selected periodic bank phase: prospective synthetic transfer, NOT physical promotion (2026-11-02)

## Evidence sequence and selection bias
[Frozen protocol](FROZEN_PERIODIC_BANK_PHASE_TRANSFER_20261102.md) committed at `bd7123e` **before** the holdout evaluator (`6292c09`), independent checker (`baf5b09`), and hosted reproduction workflow (`c726174`). The two-phase candidate was found in an exploratory **1,600-pattern search**; it is **not a prospective discovery**. The three seeds, two perturbation strengths, negative controls, acceptance thresholds, and four simple comparator policies were frozen before the new held-out evaluation.

**Evidence tier:** Local Python reconstruction of the committed service rules produced the counts below; independent 6,561-case three-bank combinational check passed locally. [Hosted full-trace independent reproduction](https://github.com/sushxnthd/vektor/actions/runs/41487158831) was **queued at report time**. These numbers must not be called hosted-confirmed until that run passes. No new RTL, matched-area route, electrical signoff, GPU IPC or RTX 5090 result is claimed.

## Frozen synthetic results (3 seeds, 1,000 warmup + 5,000 measured cycles each)
Each request consumes two bank reads, 2R/bank, four candidate slots, eight-entry FIFO, oldest must issue, four offers/cycle. The external offered source is unbounded; it is **not** on-chip hardware. Strong comparator is the best aggregate completed-work result among oldest-first greedy, reverse tie-break, least-overlap, and squared-load best-fit. All policies have the same bank ports, output cap and FIFO, **not** equal synthesized cell area or achieved clock.

| Regime | Strongest simple | Simple completed | Exact head completed | Ratio | Frozen prediction |
|---|---|---:|---:|---:|---|
| Two-phase clean | greedy (four-way tie) | 40,002 | 48,000 | **1.19994x** | >=1.10, PASS locally |
| Independent 1% operand replacement | reverse | 40,772 | 47,667 | **1.16911x** | >=1.02, PASS locally |
| Independent 5% operand replacement | reverse | 42,603 | 46,654 | **1.09509x** | exploratory, no frozen gate |
| Two-phase output cap 2 | all tie | 30,000 | 30,000 | **1.00000x** | <=1.01, PASS locally |
| IID uniform 16 banks | greedy | 57,294 | 57,306 | **1.00021x** | <1.02, PASS locally |

The clean trace reaches 3.2000 requests/cycle for exact head, versus 2.6668 for the best simple policy. The 1% perturbation yields 3.1778 versus 2.7181; 5% yields 3.1103 versus 2.8402. The no-win output-cap-2 case saturates 2.0000 for both.

The exact selected periodic stream has average read demand `d_1=d_3=d_4=0.5`, `d_0=0.375`, `d_2=0.125` per request. Thus the bank-demand necessary ceiling is 4 requests/cycle, also limited by K=4; the clean exact policy achieves 3.2. The capacity ceiling alone **does not predict** the 20% gain. The gain is due to scheduler-dependent phase locking in an adversarial periodic FIFO sequence. No compact transferable positive boundary law has yet been validated.

## Physicality and prior falsifications remain binding
The previously measured unrestricted exact selector used **5,116 generic Yosys cells and 72 logic levels**, compared with 1,613 cells and 58 levels for the rotating simple control (see [prior RTL result](RF_ROTATING_HOSTED_GENERIC_PPA_AND_TRANSFER_20261101.md)). That is a **different unrestricted RTL**, so its cost is not automatically the cost of the head-preserving selector studied here. Nevertheless, it is a strong warning: the selected synthetic 1.20x cannot be promoted until an exact age-head RTL implementation is matched to a competent control, has legal routed timing/electrical checks and a workload-derived occurrence rate. The prior integrated V317 banked-RF proxy failed electrical legality and the 2% area gate, and compact greedy physically dominated pairwise. None of these negative results are reversed.

## Audit and next kill test
- [Evaluator](rtl/periodic_bank_phase_transfer.py) and [independent full-trace checker](rtl/audit_periodic_bank_phase_transfer.py) are committed. The independent checker does not import the evaluator, replays all 75 seed/regime/policy combinations, verifies conservation and oldest-first service, and exhaustively checks 6,561 three-bank operand tuples.
- Independently checked 6,561 small-bank cases locally using a separate enumerator: PASS. Hosted full-trace replay pending.
- Next **falsification**, not promotion: randomize arrival order and inter-phase timing under frozen seeds, compare against a competent low-cost phase-aware heuristic, and derive a pre-outcome phase-conflict statistic. If the gain depends on a constructed periodic stream or equal-area RTL/timing erases it, kill the positive architecture interpretation.
- No positive-law or world-class completion claim. Do not start a second active mechanism, reset branch/PR, or overwrite prior negative evidence.
