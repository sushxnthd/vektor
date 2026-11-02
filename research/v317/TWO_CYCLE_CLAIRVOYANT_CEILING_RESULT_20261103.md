# V317 two-cycle head-preserving opportunity ceiling (2026-11-03)

**Evidence:** exact finite-batch enumeration plus independently seeded synthetic holdout; **not** GPU IPC, real bank-demand traces, synthesizable RTL PPA, legal SRAM timing, or an integrated tile. Frozen before prospective B=5 and B=16 evaluation in commit `55fff4d`. This does **not** revive V317's previously falsified physical controller claims.

## Question
The K=2 one-cycle equality result does not imply equal two-cycle completions. Is there a *measurable and pre-outcome identifiable* upper bound on gains from choosing the second issued request to avoid an incompatible residual pair? This tests a scheduling opportunity, not an implementable mechanism.

Four ordered valid requests, two operand reads/request, two ports/bank, K=2, no arrivals, two cycles. Each cycle must issue its oldest pending request. Compare compact greedy, head-preserving degree heuristic, a tail-compatibility choice, and an exhaustive two-cycle oracle. Same bank ports, issue cap, and request batch; **not** same hardware area.

## Exact opportunity law
Let `G(x)` be compact greedy's two-cycle completions for operand-bank vector `x`. Let `E(x)` indicate that (i) greedy issues head plus a partner in cycle 1, (ii) its remaining two requests cannot coissue in cycle 2, and (iii) some other head-compatible first-cycle partner leaves a coissuable residual pair. Then for **every** four-request batch:

```
C_oracle(x) - G(x) = E(x) in {0,1}
R = 1 + Pr(E) / E[G]     (population ratio of total completions)
```

**Proof sketch.** A legal first cycle can issue at most two requests and must include the head. If greedy cannot pair the head, no legal policy can do so; hence it cannot be improved by a different first-cycle choice. Otherwise greedy issues two. If the two residual requests can coissue, greedy completes all four and is optimal. If they cannot, greedy completes three; an alternative first-cycle head-plus-partner choice can reach four exactly when its two residual requests can coissue. No other two-cycle improvement is possible. This is a structural bound for this **finite batch**, not a throughput or hardware cost law.

The tail-compatibility policy checks up to three first-cycle partners, chooses the first that leaves a compatible residual pair, otherwise falls back to compact greedy. It attains the oracle in this model, but the lookahead logic, fanout, muxing, critical path, and energy are **unmeasured**.

## Frozen results

| Bank count | Evaluation | Greedy completions | Degree completions | Oracle/tail completions | Oracle/greedy |
|---|---|---:|---:|---:|---:|
| 3 | retrospective exhaustive 3^8 | 23,496 | 23,292 | 24,414 | 1.039070x |
| 4 | retrospective exhaustive 4^8 | 245,984 | 243,248 | 254,744 | 1.035612x |
| 5 | **prospective exhaustive 5^8** | 1,499,750 | 1,482,110 | 1,541,690 | **1.027965x** |
| 16 | **prospective 36,000 seeded vectors** | 143,425 | 142,770 | 143,964 | **1.003758x** |

The frozen B=5 predicted-win floor (>=1.001x) and B=16 predicted-no-win ceiling (<=1.01x) both passed. For B=16, per-seed oracle/greedy ratios were 1.003765, 1.004059, and 1.003451. The exact identity and tail-oracle equality passed on all 498,722 vectors.

The prospective 16-bank oracle improves only 539 completions across 36,000 four-request batches. This is an **optimistic upper bound** even before considering area, clock, energy, finite queue arrivals, or backpressure. The degree heuristic loses against compact greedy in all four populations.

## Audit and reproduction
```sh
python3 research/v317/rtl/two_cycle_clairvoyant_ceiling.py > /tmp/v317-ceiling.json
python3 research/v317/rtl/audit_two_cycle_clairvoyant_ceiling.py /tmp/v317-ceiling.json
```
The independently written checker enumerates feasible first/second issue sets using a separate bank-use implementation; it imports no evaluator code. Local run: **PASS**, 498,722 independently replayed vectors. Raw results are stored at `research/v317/evidence/two_cycle_clairvoyant_ceiling_20261103.json`. Hosted CI reproduction was not checked in this run.

## Decision and hard next gate
**Do not promote tail-compatibility or degree-head to a GPU mechanism.** This is a precise finite-batch opportunity ceiling, not a physical gain. The previously routed V317 RF proxy failed electrical and materiality gates, and the conflict-degree controller used 734 generic cells against compact greedy's 260. Tail-compatibility has no matched RTL area/timing evidence at all. Its apparent gain is modest for 16 uniform banks, and real operand-bank traces have not been established.

Before any new physical claim: obtain independent dynamic bank-demand traces from concrete kernels and a defensible bank mapping; freeze win/no-win trace regimes; compare compact greedy and a low-cost candidate in finite FIFO/backpressure simulation; only then require matched RTL, electrical legality, realistic wire/load, area/power, and integrated tile-level consequences. Reject any candidate whose clock/area/bandwidth costs erase the predicted advantage. Preserve this negative-control ceiling and all earlier failures.
