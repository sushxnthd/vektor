# V296 prospective latent-hotspot identifiability experiment (frozen 2026-10-25)

## Motivation and decision scope
The existing exact class-weighted admission law assumes independent slots. It has not established that a time-aggregated per-bank frequency histogram is sufficient to predict real workloads. Test the stronger counterexample: every slot has an **exactly uniform unconditional bank marginal**, with the **same within-request bank overlap** (A=B), yet an unobserved per-cycle hotspot H induces cross-slot correlation. This tests the *workload law*, not any V296-vs-serial speedup. V287 remains retired. Existing GPU holdouts are sealed and must not be accessed.

## Generative law fixed before outcomes
B=16, S=4 ordered issue slots, P=2 reads/bank, each valid independently with p=4/5. At the start of each cycle draw H uniformly from the 16 banks. Each valid slot's two source operands select the same bank X: Pr(X=H|H)=h; for each other bank Pr(X=j|H)=(1-h)/(B-1). Draw slots independently **conditional on H**. Across cycles draw H independently for the primary experiment. All individual slot marginals are exactly 1/B and Pr(A=B)=1 for all h. For each bank, at most one accepted request/cycle because its two reads exhaust both ports. The serial and V296 admission decisions are identical.

The preregistered exact prediction is

q(h) = 1-(1-p h)^S + (B-1)[1-(1-p(1-h)/(B-1))^S].

The strongest uniform-marginal IID control predicts q0=B[1-(1-p/B)^S]. This control knows the correct B, S, P, p, unconditional bank histogram, and operand overlap; it lacks the within-cycle latent-correlation statistic.

A pre-outcome observable statistic is the probability c that **two valid distinct slots in the same cycle** select the same bank:
c=h^2+(1-h)^2/(B-1).
For h>=1/B, invert it as h=[1+sqrt((B-1)(B c-1))]/B. Clip noisy estimates to [1/B,1]. Compute c on calibration requests, without examining any admission outcomes. Report both a direct known-h oracle and this diagnostic-estimated prediction.

## Frozen splits and gates
Development h: 1/16, 1/4, 1/2, 3/4, 1. Prospective unseen synthetic h: **3/8** and **5/8**. Calibration: 40,000 cycles per holdout, RNG seeds 296375 and 296625. Evaluation: 80,000 disjoint cycles per holdout, seeds 297375 and 297625. Independent concrete-bank greedy oracle must calculate observed admissions. Prediction is frozen after calibration and before evaluation. Pass if |predicted q - empirical q| <= 0.05 waves/cycle for both holdouts; the known-h exact law must agree with exhaustive concrete enumeration on small B,S cases. The independent baseline's error must be reported even if it wins. No after-the-fact threshold changes.

Use exact rational arithmetic for q; sample estimates and inversion may use floats. Report calibration c, h_hat, exact q(h), estimated q(h_hat), observed q, and baseline q0. Validate the **identifiability failure** even though the marginal bank distribution and within-request overlap are matched. A secondary block-persistent H stress test may be described only as a distinct sampling-uncertainty phenomenon; do not claim that cross-cycle correlation alone changes expected q when state resets each cycle.

## Research boundaries
Synthetic model consistency and prospective synthetic transfer only; no real GPU traces, no physical GPU tile, no power, no architectural speedup. Neither uniform-marginal failure nor a corrected law establishes novel hardware. Existing PR #13, branch, and physical evidence remain unchanged except additive findings. If results contradict the law, preserve and label falsification rather than tuning the holdout.