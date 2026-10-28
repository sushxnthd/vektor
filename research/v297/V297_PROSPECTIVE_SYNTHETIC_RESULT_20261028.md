# V297 bounded bank-rescue: prospective synthetic result and decisive limitations (2026-10-28)

**Evidence tier: SYNTHETIC THREE-REQUEST ADMISSION ONLY.** This is a new mechanism following the rejected V296 integrated GPU-performance claim. V287 and V296 are retired as positive GPU-performance candidates. This report does not establish physical feasibility, GPU throughput, energy or novelty.

## Precommitted test
The hypothesis, frozen regimes, development/holdout seeds, one-cycle cooldown, exact three-request oracle, iid prediction formula, and 0.005 waves/cycle tolerance were committed in `V297_BOUNDED_BANK_RESCUE_PREREG_20261028.md` at `21f19ea4`, **before** the evaluation script and results.

V297 examines the same three requests as priority greedy, with two register-file reads per bank and a maximum of two issued waves. If greedy admits only one, but the two younger requests are jointly feasible, it substitutes the younger pair. A one-bit cooldown forbids this substitution in the following cycle. The baseline has identical request slots, bank ports and issue bandwidth. The V297 selection logic is **not** area/timing matched yet.

For a request distribution with blocker-motif probability p and iid motifs, the exact steady-state cooldown law is r=p/(1+p) additional accepted waves/cycle. At matched frequency and no feedback/latency penalty, relative admission gain is r/Eg where Eg is baseline mean admissions. Necessary clock break-even is k=f_candidate/f_baseline > Eg/(Eg+r). The per-cycle structural improvement is exact for three requests and issue cap two; the iid stationary law is not universal.

## Executed evaluation
`node research/v297/v297_bank_rescue.js --self-test` passed locally. The simulator exhaustively checked **5,832** canonical bank/validity cases for both B=1 and B=2 (**11,664** configurations), verified exact optimal admission and bank-port safety, and detected an intentionally unsafe mutant. An independent Python implementation independently exhausted the same **11,664** configurations and audited the stored JSON. Eight seeds per regime (four development, four held-out), 100,000 cycles each, across six regimes = **4.8 million synthetic cycle observations**. All reported held-out bank-port violation counts are zero. No hosted CI result is claimed.

| Frozen regime | Dev p | Predicted extra waves/cycle | Held-out extra waves/cycle | Relative held-out admission gain | Prediction |
|---|---:|---:|---:|---:|---|
| iid 40% blocker mixture | 0.401073 | 0.286261 | 0.285943 | +17.88% | PASS (error 0.000319) |
| uniform 16 banks | 0.000850 | 0.000849 | 0.0008825 | +0.0441% | PASS |
| all requests hit bank 0 twice | 0 | 0 | 0 | 0% | PASS, no-win |
| shared issue cap B=1 | 0 | 0 | 0 | 0% | PASS, no-win |
| only first request valid | 0 | 0 | 0 | 0% | PASS, no-win |
| alternating 37-cycle bursts | 0.500570 | 0.333587 | 0.257203 | +17.15% | **iid law FAILS** (error 0.076384) |

The iid-law failure is preserved, not fitted away. Temporal clustering changes the cooldown state distribution; a scalar marginal blocker probability is insufficient. A future positive law must include a measurable pre-outcome temporal statistic or use a two-state transition model, then predict genuinely unseen burst lengths.

## Critical falsification boundary
The 17.88% figure is **offered-request admission**, not completed GPU instructions. A head-of-line request bypassed today remains pending; the synthetic exogenous generator does not carry backlog, scoreboard dependencies, cache/memory stalls, or inter-warp fairness into future cycles. A physically realistic queue could eliminate the apparent gain or change the distribution. The one-bit cooldown limits consecutive bypasses for a stable head but is not a full bounded-wait proof under changing priority. The selected pair may need additional multiplexers and wiring, and its critical path may lower clock frequency. No RF write-port, register layout, physical RC, leakage, dynamic power, or tile-level result is measured.

For the frozen iid mixture, the *conditional* clock break-even is k>0.848149, **only if** the exogenous-demand model remains valid. For uniform requests, k>0.999575; even tiny physical overhead can erase the gain. The 30,000 µm² V296 tile budget and historical routed area numbers cannot be transferred to V297.

## Prior-art bound
Bank-conflict-aware warp scheduling and elastic pipelines predate V297: Gou and Gaydadjiev (2013), DOI [10.1007/s10766-012-0201-1](https://doi.org/10.1007/s10766-012-0201-1). GPU register renumbering and bank conflict reduction are also prior art: [arXiv:2010.09330](https://arxiv.org/abs/2010.09330). The exact 3-request blocker motif and one-cycle cooldown law are a **testable analytical formulation**, not yet a demonstrated novel GPU architecture result. An expanded prior-art and patent audit remains necessary.

## Next decisive gates
1. Implement independent synthesizable V297 and optimized serial baseline RTL with the same three-slot, 16-bank, two-port, two-issue interface. Test every small-bank canonical case, randomized full-bank cases, reset/cooldown, and a persistent queue fairness/scoreboard model.
2. Synthesize both under identical library/constraints, measure logic area, critical path, fanout, routing demand and realistic load. Kill if physical frequency, area, or power pressure erases the throughput boundary.
3. Pre-register a temporal Markov transition diagnostic for bursty demand, compare against the simple marginal-p law and strong simple controls, then validate on *new* burst lengths and workloads without retuning.
4. Integrate with an occupancy/latency/bandwidth-aware tile simulator and independently audit accepted versus completed work, traffic and tail starvation. Reject any RTX-5090-equivalence claim without silicon-calibrated system evidence.

Kernellum PR #119 and prospective holdouts were not modified. V296 PR #13 retains the historical negative record; it is to be closed unmerged once the V297 draft is established. One active V297 mechanism only.
