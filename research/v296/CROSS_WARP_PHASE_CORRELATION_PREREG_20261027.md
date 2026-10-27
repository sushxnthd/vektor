# V296 cross-warp phase-correlation admission law: prospective protocol (2026-10-27)

## Physical-first scope
The matched density-0.35, 210-minute-per-contestant physical experiment #40427986118 is still running. Do not change its RTL, workflow, constraints, serial control, or frozen gates. V296 is the sole provisional mechanism; V287 remains retired. This experiment probes a **potential falsification of the existing IID four-request admission sub-law**, not physical signoff or a new GPU architecture.

## Hypothesis and mathematical prediction, frozen before holdout simulation
The existing exact four-request recurrence assumes requests are independent *across* ready warps, even if their two operands are correlated *within* a warp. Let `h` be bank-0 hotspot probability mixture, `rho` the probability that operand B copies operand A, and `s` the probability of a phase-synchronized batch. Each request consumes two reads against 16 banks with two read ports per bank; requests are visited in fixed order, with rejected requests not consuming ports.

With probability `1-s`, independently draw four requests according to the existing `exact_expected(h,rho,4)` law, denoted `Q_IID`. With probability `s`, draw one ordered bank pair and repeat it for all four ready requests. In the latter case, one request is admitted if both operands target the same bank, and two if they target distinct banks. For `p_0=h+(1-h)/16`, `p_i=(1-h)/16` for i>0:

```
P_same = rho + (1-rho) * sum_i p_i^2
Q_sync = 2 - P_same
Q(h,rho,s) = (1-s) Q_IID(h,rho) + s Q_sync(h,rho)
```

This is an exact law **for the stated mixture generator**, not a measured hardware law. It predicts a strict loss with growing s whenever Q_IID>Q_sync. In particular, two generators can have identical per-request bank marginals and within-request rho, yet very different admissions. Therefore the IID law cannot transfer to phase-correlated traces based only on h and rho.

## Frozen regimes and prospective holdouts
Use the preexisting exact dynamic program without fitting, plus a separately implemented explicit-bank Monte Carlo oracle with four requests and two read ports per bank. Regimes `(name,h,rho,s)`:

1. uniform_control (0,0,0)
2. uniform_partial_sync (0,0,0.25)
3. uniform_strong_sync (0,0,0.8)
4. moderate_hotspot_sync (0.45,0.2,0.65)
5. heavy_hotspot_sync (0.8,0.2,0.95)

Holdout seeds **20261031, 20261101, 20261102**; **30,000 batches per cell** (15 cells, 450,000 total). Evaluate no cells before this protocol is committed. Primary tolerance: absolute error of Q versus independent oracle <= **0.035 admissions/batch** for every cell. Negative-control requirement: s=0 exactly recovers Q_IID. Falsification: the uncorrected IID-only law must have >=0.25 admissions/batch error for both uniform_strong_sync and moderate_hotspot_sync; otherwise the claimed transfer failure is not demonstrated by these chosen regimes. Report every seed, including failures.

## Evidence and limitations
Implement an independent oracle that never calls the dynamic-program transitions for individual event outcomes; it uses explicit bank counters. Include exact boundary/invalid-input tests, a machine-readable result and an independent audit of the aggregate. This is a mechanistic stress test of bank-admission prediction; **not** evidence that V296 outperforms optimized serial arbitration, is physically routable, improves GPU throughput, or has a novel probability theorem. Real warp traces could exhibit different correlation structures and require independently estimated s or a richer model. Preserve unopened real-workload holdouts. Kernellum PR #119 and its existing experiments remain untouched.
