# V317 RF-bank arbiter audit: failed physical-overgrant prediction, real greedy scheduling gap (2026-11-01)

**Decision: reject the preregistered overgrant hypothesis.** The existing `rtl/vtile/rf_bank_arbiter.sv` already charges **two** read ports for a same-bank source pair by setting both `used_once` and `used_twice`. The initial source inspection missed that detail. This failed prediction is preserved in [the frozen protocol](FROZEN_RF_ARBITER_SAME_BANK_PORT_AUDIT_20261101.md), committed at `7cc2d4b` before the checker and results. No RTL change is warranted on this evidence.

## Independent check

The executable [source-level oracle](rf_arbiter_port_audit.py) translates the original four-slot fixed-priority arbiter, then independently counts **both** operand reads against two physical read ports per bank, even when source-bank indices match. It also enumerates all 16 subsets of four requests to obtain an exact maximum-cardinality issue subset at the **same bank and port resources**. The maximum-cardinality scheduler is a *mathematical upper bound*: its selection network, latency, area and control power are not costed.

| Regime | Cases | Physical overgrants | Cases greedy loses to exact subset | Sum greedy grants | Sum exact grants |
|---|---:|---:|---:|---:|---:|
| Exhaustive 2-bank, 4-slot, all valid masks and operand-bank pairs | 4,096 | **0** | **244** | 5,210 | 5,454 |
| Fixed-seed 4-bank random transfer | 10,000 | **0** | **178** | 16,428 | 16,606 |

The aggregate exact-subset opportunity is `5454/5210 = 1.0468` on the exhaustive two-bank enumeration and `16606/16428 = 1.0108` on the random four-bank cases. These are **per-decision grant-count ratios on synthetic distributions**, not IPC speedups or realizable tile throughput.

The frozen **predicted-fail** case, two same-bank double-read requests, *passed* the physical-port oracle: the RTL grants only one request, using exactly two ports. The frozen predicted-pass case, two requests using different banks, grants both safely. The 4,096-case sweep showed maximum granted demand of exactly two reads per bank.

The first genuine scheduling counterexample has three valid requests with bank pairs `[(0,0),(0,1),(0,1)]`: fixed priority grants slot 0 alone, while the equal-resource maximum-cardinality scheduler grants slots 1 and 2 simultaneously. This is an **issue-selection inefficiency**, not a physical violation and not evidence of a novel V317 register-forwarding mechanism.

## Reproduction

```bash
python -m unittest research.v317.test_rf_arbiter_port_audit -v
python -m research.v317.rf_arbiter_port_audit
```

Six local tests passed on the committed implementation; the full sweep completed locally. The source model and independent bank-demand oracle agreed across every case. Hosted CI should be evaluated separately at the final commit.

## Research boundary

The existing arbiter's conservative two-read accounting is physically sensible **under the assumed two-read-port-per-bank model**. The model does not establish the actual bank-port count of a target GPU, register file circuit, dynamic operand identity, read timing, compiler issue semantics, collector buffering, or routed electrical behavior. The optimistic scheduling gap must be compared against a real implementable equal-area and equal-frequency scheduler before promoting any architecture claim.

This is a baseline-validation and falsification instrument within the existing V317 draft PR, not a new active mechanism. V317 forwarding remains killed by the same-information baseline. Historical V296 physical/electrical and V287 retirement decisions are unchanged. Kernellum PR #119 is untouched. No measured GPU speedup, silicon timing signoff, or RTX-5090 equivalence is claimed.
