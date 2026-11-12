# V314 prospective falsification: completion-hint bank arbitration is not material

**Decision 2026-10-31: RETIRE V314 before RTL.** Frozen preregistration commit: `e861c17250c01f62563732377e558eb5b51f7327`. Source-pinned independent hosted evidence: [Actions #41192071316](https://github.com/sushxnthd/vektor/actions/runs/41192071316), success, including the separate per-bank event checker. Earlier [Actions #41192020744](https://github.com/sushxnthd/vektor/actions/runs/41192020744) independently passed the same frozen outcomes before adding the bank-pressure audit.

## Mechanism and strong control

V314 gives an RF read priority when the instruction's other source operand has already been collected, with an age shield after 16 cycles. The comparator is a **buffered, bank-aware, early-capable, oldest-first operand collector**, with the same four warp slots, four entries/slot, sixteen banks, two read ports/bank/cycle, two distinct physical-register operands/instruction, ready-first service, and residual-port early reads. Identical pre-generated offered traces feed both policies. The model contains no real GPU trace or RTL timing.

## Frozen 20,000-cycle held-out results (2,000-cycle warmup)

| Regime / seed | Baseline completed | V314 completed | Ratio | p99 baseline -> V314 | Bank 0 reads baseline / V314 |
|---|---:|---:|---:|---:|---:|
| Predicted small win / 314801 | 35,900 | 35,812 | **0.997549x** | 11 -> 13 cycles | 40,000 / 40,000 |
| Predicted no win / 314802 | 56,017 | 56,017 | **1.000000x** | 2 -> 2 | 6,956 / 6,956 |
| Unseen transfer / 314803 | 34,763 | 34,775 | **1.000345x** | 12 -> 14 | 39,991 / 39,996 |
| Dependency sensitivity / 314804 | 32,590 | 32,552 | **0.998834x** | 12 -> 14 | 40,000 / 40,000 |

The preregistered hotspot prediction of 1.0005-1.004x was **falsified**, not retrospectively rewritten. The 1.02x materiality gate fails, and p99 worsens from 11 to 13 cycles. The no-win prediction passes exactly. The unseen transfer stays inside its broad prediction interval but delivers only 0.0345% improvement and a worse tail. The dependency regime also regresses.

The independent checker verified every measured cycle: no more than two reads per bank, no duplicate operand service, at most four completions/cycle, exact aggregate RF read accounting, and workload conservation across finite FIFOs. These are simulator invariants, not electrical signoff.

## Mechanistic capacity boundary (within this model)

Let `R_b(T)` be measured reads served from bank `b` in `T` cycles. With two ports per bank,

```
R_b(T) <= 2T.
D_b(completed) <= R_b(T) + 2 * SLOTS * DEPTH
```

The second inequality allows at most 32 pre-warmup operand reads for jobs already buffered when measurement starts. Here `T=20,000`, so bank 0's read budget is 40,000. **Both policies consume all 40,000 bank-0 reads in the hotspot and dependency regimes.** The transfer baseline consumes 39,991, and the candidate 39,996. In the hotspot, bank-0 demand from completed instructions is exactly 40,000 for both, matching measured service.

Consequently, this particular completion-priority rearrangement does not relieve the binding bank-0 service limit. It may change which jobs complete and tail latency, but cannot create bank-0 bandwidth. For an unbiased stationary instruction mix with expected bank-0 read demand `d_0` per completed instruction, the fluid throughput ceiling is `min(4, 2/d_0)` instructions/cycle. This approximation is **not** an unconditional bound under policy-dependent job selection; the exact finite-horizon accounting inequality above is the audited statement.

## Research implications and limits

The earlier V309/V312 physical failures and V313 prior-art kill already make additional arbitration-only proposals low priority. V314 adds direct prospective evidence that a low-cost completion hint can lose even against a strong early-capable buffered baseline while the hot bank remains fully occupied. A future mechanism must demonstrably **reduce effective hot-bank demand, redistribute actual physical read capacity, or exploit a real measured workload bottleneck**. Any scheduler-only claim requires a same-information, equal-resource collector and tail-safety evidence.

**No RTL, synthesis, matched area/timing, routed RC, electrical checks, power, real workload throughput, novel architecture, or RTX 5090 equivalence was established.** V314 is retired; preserve the negative result and do not promote it.
