# V317 frozen matched routed-load and area-phase falsification (2026-11-02)

## Research status and immutability
Continue the single active **pairwise fixed-priority bank-credit implementation** on `research/v317-sass-provenance-gate`, PR #34. This is a **grant-equivalent control-block optimization**, not a new scheduling policy. V287 and V296 remain historical. This protocol precedes the new workflow and area-phase checker. Do not change these predictions after inspecting results. Preserve failed routes.

## Physical experiment: output-load transfer
Use the existing 40-FF registered source/pairwise wrappers, official pinned ORFS image `openroad/orfs@sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8`, Nangate45 typical, **identical** 60x60 um die / 52x52 um core, 2.0-ns clock, BUF_X2 input drive, 0.1-ns uncertainty, and matched input/output delays. Re-run both designs with two output loads **10 fF** (replication control) and **40 fF** (unseen routed load), each with its own complete ORFS work directory. Change only `set_load` in a copied SDC. Do not claim timing from any incomplete or electrically illegal route.

Predictions fixed before outcomes:
- P1: At 10 fF both source and pairwise route with zero DRC, setup/hold and max-slew/cap/fanout violations; pairwise final cell area below source and pairwise routed minimum period below source.
- P2: At 40 fF **do not presume electrical legality**. The preregistered **no-architecture-win** control is 1.000x intrinsic completed service at equal clock, RF ports, and grants, whether or not the route succeeds. A failed 40-fF route is negative physical evidence, not missing data to silently exclude.
- P3: If 40-fF pairwise route succeeds, pairwise must retain positive **routed** minimum-period and standard-cell-area margins to survive as a low-cost implementation. If it fails max-slew/cap/setup/hold/DRC, label the load point **NO-GO** regardless of raw delay. Repeated 10-fF control must reconcile with prior area/period within 10% or the experiment is inconclusive.
- The 40-fF load is an electrical stress test, not a second process corner or a real RF-bank load estimate. No power, GPU IPC or multi-corner signoff claims.

## Analytic resource-reinvestment boundary
Use *measured* equal-footprint rounded routed control-block areas `A_s=1316` and `A_p=583` um2, and periods `T_s=1.56`, `T_p=0.58` ns as provenance-pinned illustrative inputs, with explicit **hypothetical** other tile area `A_o` and critical path `T_o`. For `n` source tiles, let the total budget be uniform over one source-tile area interval `[n(A_o+A_s),(n+1)(A_o+A_s))`. The exact fraction of budget phases where pairwise fits at least one more tile is

`P_extra = clamp((n+1)(A_s-A_p)/(A_o+A_s),0,1)`.

This follows from floor division; it is **not** a probability of performance gain on real GPUs. For finite budgets, compute exact integer tile counts rather than assuming a one-tile maximum. Throughput is `min(offered, bandwidth, tiles * work_per_tile_cycle / max(T_o,T_arbiter))`. No intrinsic service-per-cycle difference.

Prospectively frozen test regimes:
- W1: `n=24, A_o=40000, T_o=2.0 ns`, with unlimited offered load/bandwidth. Expect exact extra-tile budget-phase fraction `18325/41316 ≈ 0.44353` and, only in the extra-tile phase, a `25/24` modeled throughput gain. For a budget exactly `24*(A_o+A_s)`, expect **no win**.
- N1: Same `n,A_o,T_o`, but shared bandwidth capped below source compute capacity. Expect **1.000x** modeled throughput at all budget phases, including those fitting extra tiles.
- Transfer holdouts (not used to fit law): `(n,A_o)=(17,100000),(32,80000),(48,200000)`; require the exact phase law to agree with exhaustive integer-budget enumeration to tolerance `1/(A_o+A_s)` or better. Also check `n=24,A_o=40000` with `T_o=1.0` to isolate the clock-critical conditional win.
- A strongest equal-resource control is the source implementation under the *same* total area budget and shared bandwidth, with exact integer tile count. Do not assign the pairwise implementation extra bandwidth, ports, or issue slots for free.

## Kill and evidence policy
Kill any claim of unconditional GPU IPC gain. Retain implementation only if matched physical load points are electrically admissible, area advantage survives, and independent checker reproduces raw artifacts. If routing invalidates the physical advantage, report NO-GO. A conditional budget-phase accounting law is not a novel microarchitecture result. Preserve source SHA, tool digest, logs, artifacts and failures. Kernellum PR #119 remains separate and untouched during this urgent primary gate.
