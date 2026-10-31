# V317 bounded-collector exact-service result (2026-11-01)

**Decision: retain V317 as a falsification/evidence instrument; do not promote hypothetical B-read elimination to hardware.** This report corrects a **failed preregistered prediction**, establishes an exact occupancy threshold for a restricted two-class model, and validates it on frozen count holdouts. It is not a GPU speedup.

## Provenance and methods

- Initial protocol frozen first at [93a1edc](https://github.com/sushxnthd/vektor/commit/93a1edc7b975e88d4832738d9a68d618099b17c4), **before** implementing the solver. Its incorrect K=1 prediction remains unedited.
- Exact breadth-first shortest-path scheduler and independently coded trace validator at [2e78973](https://github.com/sushxnthd/vektor/commit/2e78973e3b61be100c68b871ebc5b9bbee60e933). Independent depth-limited reachability checks small worlds without calling the scheduler transition function.
- Frozen regime and adversarial tests at [fe78860](https://github.com/sushxnthd/vektor/commit/fe78860c0460edd9670da646f0a8974639971bea).
- **Second** prospective two-class law protocol frozen at [03682d5](https://github.com/sushxnthd/vektor/commit/03682d575f33c513a0b5e773ae1fe458dd57fb99) after the initial pilot but before opening the specified new count holdouts; 72-world checker at [27b9f93](https://github.com/sushxnthd/vektor/commit/27b9f9360ec6bd357f8beecae05b29cc4f1a769e).
- Reproduction: `python -m unittest research.v317.test_bounded_collector_exact research.v317.test_two_class_collector_law -v`; `python -m research.v317.bounded_collector_evidence > bounded_collector.json`. The V317 hosted audit workflow now includes these tests and uploads the JSON with the source commit.

## Matched synthetic service model

Three banks A/B/C, one read port each; two completions/cycle; K in-flight collector entries per design. Each instruction may have several independent bank operands read in **one** cycle. Different operands can also be staged across cycles. Optimal arbitrary admission and read scheduling is allowed for **both** designs, with the same K and ports. The baseline has classes AB, BC, CA; the **hypothetical unimplemented** candidate has A, BC, CA. All operands are initially ready; no RF-cache reuse, forwarding, dependencies, real physical bank mapping, power, control or clock overhead.

## Frozen and unopened results (minimum service cycles)

| World (a,b,c), K | Baseline | Candidate | Gain | Interpretation |
|---|---:|---:|---:|---|
| (2,2,0), K=2 | 4 | 2 | 2.000x | frozen predicted win survived |
| (2,2,2), K=4 | 4 | 4 | 1.000x | frozen predicted no-win survived |
| (2,1,0), K=2 | 3 | 2 | 1.500x | frozen transfer survived |
| (2,2,0), K=1 | **4** | **4** | **1.000x** | **frozen 8/6 prediction falsified** |
| (3,2,1), K=2 | 5 | 4 | 1.250x | unopened transfer |
| (1,3,2), K=3 | 5 | 5 | 1.000x | unopened transfer |
| (3,0,3), K=2 | 6 | 6 | 1.000x | unopened transfer |

The original protocol predicted K=1 baseline 8, candidate 6 cycles (1.333x), incorrectly serializing different-bank reads for the same instruction. In the actual preregistered bank-parallel model, one collector entry can finish one AB or BC instruction in a cycle. Thus both policies finish N instructions in N cycles, with **zero** improvement. The wrong prediction is preserved rather than silently revised.

## Exact positive boundary law, restricted to c=0

For a AB and b BC instructions, N=a+b>0, K>=1:

    T_baseline = N
    T_candidate = N               if K=1
                  max(a,b)        if K>=2

    G(a,b,K) = 1                  if K=1
               (a+b)/max(a,b)    if K>=2

**Proof within the model.** K=1 permits at most one completion/cycle; each class has distinct source banks and can complete in one cycle. For K>=2, every baseline instruction needs B, so the single B port requires N cycles, achievable by servicing one instruction per cycle. Candidate AB uses only A while BC uses B and C, so a pair can finish together with two collector slots, achieving max(a,b) cycles; the individual A and B/C port demands also lower-bound the result. This is a **collector-occupancy phase boundary**, not an invented GPU physical law.

The second protocol's unopened holdouts passed:
- (4,3,0): K1 7/7, K2/K3 7/4.
- (5,2,0): K1 7/7, K2/K3 7/5.
- (1,4,0): K1 5/5, K2/K3 5/4.
- (0,5,0): all K 5/5.

The complete a,b in 0..4 (nonempty), K=1..3 sweep checked **72 worlds with zero mismatches**. The independent reduced-domain depth-limited reachability oracle checks that no shorter schedule exists; trace replay checks collector overflow, per-bank ports, admission, exactly-once reads, and completion width. Local focused regression: 5 tests passed. Hosted status must be verified separately; do not equate existing RTL CI with candidate RTL.

## Collector sensitivity and physical consequences

| World | K=1 gain | K=2 gain | K=3..6 gain |
|---|---:|---:|---:|
| (2,2,0) | 1.000x | 2.000x | 2.000x |
| (2,2,2) | 1.000x | 1.000x | 1.000x |
| (2,1,0) | 1.000x | 1.500x | 1.500x |
| (3,2,1) | 1.000x | 1.250x | 1.250x |
| (1,3,2) | 1.000x | 1.000x | 1.000x |
| (3,0,3) | 1.000x | 1.000x | 1.000x |

An optimistic gain can disappear at K=1 even with genuine read elimination. Conversely K>=2 only helps if both affected instruction classes compete for B and their A versus B/C demands can be overlapped. This makes occupancy/collector budget a necessary predictive variable, beyond average bank demand alone.

For the restricted two-class model, if candidate control adds C service-equivalent cycles and its clock period grows by factor 1+delta, a **conditional** gain above 1.02 requires:

    (a+b) / ((max(a,b)+C)*(1+delta)) > 1.02, K>=2

This is a feasibility inequality, not a measured timing estimate. Cache hits, rematerialization, instruction dependency timing, realistic RF bank mapping, and a strong compiler baseline may eliminate the proposed read savings entirely.

## Decision and remaining gates

The candidate's B-read removal is **not implemented**. No source register may simply be deleted without a functional equivalence proof; no matched RTL, synthesis, electrical checks, area/power or workload-level GPU IPC has been produced. No claim of architectural novelty or RTX 5090 equivalence is supported. V317 remains a bounded evidence/falsification branch; do not treat the ideal 2.000x service-cycle ratio as a GPU performance result.

Next: obtain provenance-pinned real compiled SASS and dynamic bank/cache measurements, then compare an implementable read-reduction mechanism against reuse-aware, buffered, compiler-rematerializing equal-resource controls. If real RF traffic is not B-critical, or clock/area/port penalties erase the gain, kill it before further RTL work. Preserve all negative results and the existing PR.
