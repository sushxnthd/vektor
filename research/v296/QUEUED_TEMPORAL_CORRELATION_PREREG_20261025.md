# V296 queued-bank temporal-correlation prospective protocol (frozen 2026-10-25)

**Scope:** A workload-level falsification of the previously validated independent-cycle admission law. Not a new GPU mechanism, RTL timing measurement, or evidence of V296 speedup. V296 is the sole active mechanism; V287 remains retired. Existing GPU workload holdouts stay sealed.

## Hypothesis, before outcomes

With 16 banks, four ordered issue queues, two read ports/bank, per-slot Bernoulli arrivals p=0.8, conditional per-cycle hotspot probability h=0.75, and FIFO depth Q=8, the hidden hotspot bank H follows H_t=H_(t-1) with probability s, otherwise is redrawn uniformly. Each arrival chooses H_t with probability h and another bank uniformly otherwise; each request reads the selected bank twice. Thus every slot's bank marginal remains uniform, within-cycle conditional collision c=h^2+(1-h)^2/15 remains identical, and raw-arrival expected admission under an empty-per-cycle model remains identical for every s. **Persistent queues can make actual accepted work depend on s**, because head-of-line blocking couples consecutive cycles.

The request-only cross-cycle collision law is d=s*c+(1-s)/16, where d is the probability two independent requests in adjacent cycles hit the same bank. Estimate c from same-cycle pairs, d from adjacent-cycle pairs, p from arrivals, then infer h=[1+sqrt(15*(16*c-1))]/16 and s=(d-1/16)/(c-1/16), clipped to valid bounds. All diagnostic statistics use *raw arrival banks before arbitration*, never admissions. The predictive FIFO model is a deterministic-seeded, cycle-accurate replay at inferred (p,h,s); a strong simple control uses the same queues and inferred (p,h) but assumes s=0. A second control is the prior no-queue exact admission law. The FIFO model is a **generative simulation**, not a compact closed-form throughput law.

## Frozen evaluation

- Development-only s values: 0 and 0.9; no fitting on holdout admissions.
- **Unseen synthetic holdouts:** s=0.35 (seed 296350) and s=0.95 (seed 296950).
- Per holdout: 50,000 independent calibration arrival cycles; 10,000 warm-up + 80,000 measured evaluation cycles with evaluation seed 297350 or 297950; independent predictor seed 298350 or 298950, same warm-up/evaluation lengths.
- The baseline and prediction use *the same independently inferred p and h*; only temporal s differs. Report empirical admissions, offered arrivals, drops, queue occupancy, pairwise-vs-serial decision mismatches, predictor and baseline errors.
- Precommitted pass gates: candidate prediction absolute error <=0.08 admissions/cycle on both holdouts; >=50% reduction in absolute error against the s=0 queued baseline on both holdouts; zero serial/pairwise mismatches on every evaluated cycle; per-bank read-port accounting, queue conservation, and reproducible fixed-seed output.
- Negative result must be preserved if any gate fails. No threshold or seed changes after evaluation. Only one run should be spent on packaging/plumbing.

## Physicality and novelty limits

V296 and serial one-hot implement the same priority-greedy bank admissions under this two-reads-same-bank traffic restriction, so at matched clock, queues and bank resources **their throughput is exactly identical**. A temporal-workload predictor can improve performance *estimation* but does not create an architecture gain. Any future speedup requires measured integrated tile frequency, energy, or resource reinvestment against an equal-consumed-area control. Real traces may not satisfy this latent-hotspot Markov family. No RTX-5090 equivalence or novel Markov-chain theory is claimed. The earlier frozen win/no-win physical tile boundaries remain unchanged.
