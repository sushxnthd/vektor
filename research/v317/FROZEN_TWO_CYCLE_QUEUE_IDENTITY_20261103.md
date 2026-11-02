# Frozen V317 two-cycle queue-identity challenge (2026-11-03)

## Prior result and problem
The existing packed-FIFO theorem proves that, with a valid oldest request and output cap K<=2, compact greedy, degree-head and exact-head produce the same **instantaneous grant count**. It does not prove identical selected identities, residual queue state or finite-horizon throughput. Degree-head has previously synthesized to 734 generic cells versus 260 for compact greedy; its integrated physical case remains falsified.

## Mechanism under attack
Do not promote a new architecture mechanism. Attack the existing V317 degree-head scheduler using the same four-slot two-read-per-request, two-read-ports-per-bank abstraction. All four requests are valid and resident at t=0. At t=1 no new requests arrive. Both schedulers must serve the oldest request; issue cap K=2. Compare completed requests after **exactly two cycles**, not eventual drain time. Equal physical bank resources and identical offered batch. First-cycle cardinality is predicted to be identical; second-cycle service may differ because residual identities differ.

## Prospective predictions frozen before B=4 evaluation
1. For every all-valid four-request B=4 vector, first-cycle compact greedy and degree-head grant cardinality must agree.
2. For 40,000 independent uniformly random B=4 four-request vectors at each of seeds 503, 907, 1201, degree-head will complete **fewer** requests by the end of cycle 2 in aggregate than compact greedy, with aggregate ratio <=0.995. A ratio >0.995 falsifies the material-negative prediction.
3. An independent checker must reproduce the per-seed totals and prove the exact per-batch two-cycle residual-conflict identity; any mismatch invalidates the result.
4. Retrospective exhaustive B=3 (3^8=6,561 all-valid batches) is reported separately, without pretending it is unseen.

## A priori predictive identity
If first-cycle grant masks are equal, both policies have identical two-cycle outcomes. If they differ, both first serve two requests and leave two. For each policy p, let I_p=1 when its residual pair cannot coissue under the same two-port bank constraints, otherwise 0. Then exactly
  C_degree(2)-C_greedy(2)=I_greedy-I_degree.
This is an exact **finite-batch** service identity and is not a predictive population model until residual conflict rates are independently predicted on unseen workloads. We will verify the identity on every vector, not fit coefficients.

## Falsification and evidence limits
If degree loses on the unseen B=4 test, its K=2 snapshot equality is insufficient to support a queue-level no-win theorem, and the controller is strictly weaker on this finite-horizon population despite 2.82x generic cell cost. If degree wins, preserve the contradictory evidence. No results are GPU IPC, realistic wave traces, mapped power, routed area, electrical legality, or RTX 5090 evidence. This test does not replace the current PR, branch or physical kill gates.
