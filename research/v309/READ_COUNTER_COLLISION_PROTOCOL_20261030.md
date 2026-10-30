# V309 read-counter collision impossibility protocol (2026-10-30)

**Tier:** retrospective structural falsification on an already inspected published GV100 sample. This is NOT prospective, matched, or a GPU speedup. Preserve V309 qualification branch, PR #26, and all retired hardware decisions.

## Frozen question
Can *any deterministic function*, linear or nonlinear, of read-only counters `(L1_RH, L1_RM, L2_RH, L2_RM)` exactly reconstruct the published `DRAM_Rd` value on all 25 rows? Compare to the weaker feature pair `(L1_RM,L2_RM)` and the stronger full four-counter set. Do not use kernel names, write counters, elapsed cycles or target values as predictor features.

## Source and immutable identity
Use the already audited Accel-Sim sample GV100 profiler CSV at commit `7ba54ded60c4ba0083410c37d22d719166acd6dc`, Git blob `aa88bb2566ff3b3e012442cd20bc753127732cac`. Reuse the existing strict parser and its SHA check; no unpinned network inputs.

## Test and mathematical law
Group rows by exactly equal Decimal read-counter vectors, retaining all zeros. For each group with at least two *different positive* DRAM_Rd values, calculate `y_min`, `y_max`, ratio `R=y_max/y_min` and the **sharp minimax multiplicative lower bound** `sqrt(R)`. For any fixed positive prediction `p` on a collision, `max(p/y_min, y_max/p)>=sqrt(R)`; equality is reached at `p=sqrt(y_min*y_max)`. This is an information-theoretic non-identifiability bound for that restricted feature set on this published sample, NOT a physical-law speedup or a statistical generalization claim.

Before running the code, the inspected sample suggests that `binomialOptions` and two `quasirandomGenerator` kernels share a four-counter zero vector while DRAM_Rd differs; this is **not an unseen prediction**. A strong oracle comparator is the *best possible* groupwise constant predictor, which must still obey the bound. Also compute the additive minimax lower bound `(y_max-y_min)/2` as an independent scale check.

## Independent verification and kill gate
1. Separate O(n^2) pairwise oracle checks the strongest-collision range without reusing the grouping implementation.
2. Synthetic fixtures test noncollision, same-target collision, distinct-target collision, exact Decimal equality, and nonfinite/negative input rejection via existing parser.
3. Assert exact rational squared lower bound `R` to avoid relying on floating rounding. Report sqrt as display only.
4. If no collision survives in the full four-read-counter feature set, kill the stronger claim and report only the two-counter result.
5. If collision survives, kill **all deterministic read-only-counter-to-DRAM_Rd exact estimators on this sample**, not the possibility of models with extra features, richer provenance or probabilistic errors. Never treat read-counter units as bytes.

## Scope limits
The CSV is not matched to V309's Rodinia 2.0-ft SASS archive. Counter collection/aggregation semantics are not independently authenticated. Do not join the sources, infer GPU throughput, revive V287/V296, promote new hardware, or claim novelty beyond this bounded identifiability certificate. Next hardware gate remains matched source-authenticated traces and profiler counters plus cycle/RTL validation.
