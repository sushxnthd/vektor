# V309: prospective issue-admission boundary law and workload-regime holdout (2026-10-31)

**Status: frozen before the held-out generator seeds are evaluated.** This protocol concerns the **same** maximum-cardinality bank-admission mechanism as the factored RTL, not a new architecture. The brute-force enumerator was already killed at the frozen 2.0x generic-cell gate. **If the factored RTL also fails that gate, these workload results cannot rescue it.** This is synthetic issue-admission modeling, not GPU throughput or physical validation.

## Derivation and falsifiable boundary

Four ordered requests, two operand reads each, 16 banks, two read ports/bank, fixed-priority greedy incumbent G and maximum-cardinality M with smallest-numeric-mask tie break. For any request vector, both must be feasible and `0 <= popcount(M)-popcount(G) <= 1`. The upper bound follows because: (i) if greedy grants two, an optimal grant of four would imply all requests jointly feasible and greedy would grant four; (ii) if greedy grants one, three mutually feasible other requests cannot all be blocked by that one two-operand request without requiring three reads on at least one of its at-most-two banks; and (iii) greedy grants zero only when no request is valid. This is a property of this restricted four-slot, two-port contract, **not a general GPU theorem**.

Define the observable conflict-loss event `L = 1[popcount(M)>popcount(G)]`, the pilot/holdout mean greedy issue count `g=E[popcount(G)]`, and `p=Pr(L)`. The **exact per-opportunity admission law** is `m=g+p`; issue-admission ratio `R_issue=1+p/g` for `g>0`. This is a conservation identity and must not be advertised as a novel predictive law. For downstream per-cycle acceptance cap `B`, a deliberately **optimistic** static throughput envelope is `R_cap=min(B,g+p)/min(B,g)`. If the candidate requires an extra pipeline stage, has frequency ratio `f_candidate/f_greedy`, incurs issue-control overhead `c`, or changes occupancy/queue distributions, these effects must be measured and incorporated; the naive issue ratio is *not* an end-to-end speedup.

## Disclosed exploratory pilot and prospective held-out regimes

An exploratory, non-held-out 20,000-opportunity simulation at seed 20261031 found about 0.12% admission-ratio improvement with independent uniform bank IDs, and 4.37% with 80% probability of sampling one of three hot banks (otherwise uniformly among 16). This pilot was inspected **before** this protocol; it cannot be counted as prospective evidence.

Freeze the following unseen generators and directional gates, before their results are computed:

| Regime | Bank sampling per operand | Validity | Holdout seed | Prediction |
|---|---|---|---|---|
| Predicted no-win | 16-bank uniform iid | all four requests valid | 0x309C | `R_issue < 1.01` |
| Predicted win | 80% iid from banks 0,1,2; 20% iid uniform over 16 | all four valid | 0x309D | `R_issue > 1.02` |

Use **20,000 opportunities per holdout**, Python `random.Random(seed)` and fixed generator call order: for each opportunity generate all eight operands in slot order, source0 then source1, first Bernoulli hot-set choice then uniform bank choice; no outcome-dependent selection. Report full `(G,M)` joint histogram, `p`, `g`, `m`, exact-law residual, and predicted/no-win gate. Verify the independent brute-force subset oracle against the separately coded greedy controller, and assert the per-opportunity gain is either 0 or 1. Include all four-slot/port constraints and full 16-bank address domain.

**Independent evaluation requirement:** the law's prediction is arithmetic given observed `p`, not independent out-of-sample prediction of `p`. The true architecture result additionally requires predicting `p` from pre-outcome trace features or a frozen generator model, independent real-workload traces, matched-resource physical frequency, occupancy/backpressure, bandwidth/port pressure and control overhead. The holdouts here can only validate a narrow synthetic issue regime and the mathematical identity. Reject any claim of novel GPU speedup or tile-level gain from these results alone.
