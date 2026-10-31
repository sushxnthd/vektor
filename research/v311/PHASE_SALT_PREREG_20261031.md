# V311 prospective kill test: phase-cohort register-bank salting (2026-10-31)

## Single candidate and physical semantics
Candidate: assign a **warp-lifetime-immutable** XOR bank salt at *new warp/cohort allocation*; all reads and writes to that warp's physical registers use the same salt. No mid-warp remapping or free data migration. The test is deliberately limited to a two-warp, one-register-read-per-warp issue opportunity with **16 banks, one read port per bank**; it is NOT a four-slot/two-read V-Tile model, nor a GPU speedup. The reuse-aware fixed-priority baseline is unchanged. Existing V287/V296/V309/V310 no-go evidence is preserved.

Compare:
A. strongest global **offline-optimal fixed XOR salt**, selected with complete knowledge of the workload's phase mixture (stronger than a naïve static hash);
B. phase-cohort **oracle** selecting a salt separately for each newly launched cohort;
C. the proposed histogram-selected per-cohort salt. If C cannot beat B with the same phase information, do not claim selection-algorithm novelty. This is a capability ceiling, not equal silicon area.

## Frozen positive/no-win regimes and holdouts
- B=16 banks. Each operand bank is independent with hot-bank probability 0.85 and remaining 0.15 uniformly on the other 15 banks. Warp A's hot bank is 0.
- **Predicted-win**: 16 equal-duration *freshly launched* cohorts; warp B's hot bank rotates through 0..15. Static baseline must use ONE salt across all cohorts; cohort candidate may change salt only at launch. Each cohort has 25,000 independent held-out issue opportunities, seeded with 311000 + cohort index.
- **Predicted-no-win**: 16 cohorts all with warp B's hot bank 0; same samples and seeds, static oracle may select its optimal salt.
- Training/selection uses exact declared probability mass functions, never held-out samples. For ties, choose the lowest salt.
- Compute predicted admitted requests/opportunity exactly as E[admit]=2-C, where C(s)=sum_b p(b)q(b XOR s). Count 1 if banks collide, otherwise 2.
- Holdout acceptance: candidate/static gain within 0.01 of prediction in each regime, stationary no-win gain within 0.01 of 1; candidate and phase oracle identical decisions on all held-out samples; no drop/loss of reads.
- Physicality **kill boundary**: candidate must exceed 1.05x ideal admitted work over strongest static control in the predicted-win regime BEFORE any extra selector area, power, clock, bank-encoding delay or occupancy. If below 1.05x, retire this *narrow mechanism/regime* without RTL implementation. This is an engineering materiality threshold, not a universal theorem. Never infer tile throughput from admission ratios.

## Mechanistic limitation and prior art
A bank XOR is a bijection, so intra-warp collisions are unchanged. Benefits can arise only from inter-warp collision changes at cohort boundaries. Bank coloring, bank-aware register allocation, XOR hashing and warp scheduling have substantial prior art; novelty is **unproven**. Strong equal-capability dynamic salt allocation may eliminate any claimed incremental novelty. An actual successor would require complete RF read/write datapath, equal-resource RTL, routing, electrical and workload tests.

## Independent audit requirements
The checker must separately recompute expected collision probabilities and simulate bank-address pairs, reject nonbijective salt maps, reject any salt change during a live cohort, and verify the fixed oracle really minimizes mixture collisions. Preserve failed predictions and negative results.
