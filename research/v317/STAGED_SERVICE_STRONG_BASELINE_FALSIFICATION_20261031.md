# V317: staged operand service changes the atomic coissue conclusion (2026-10-31)

**Decision:** the previously reported **1.500x** synthetic advantage of a hypothetical AB->A bank-read removal at (AB,BC,CA)=(2,2,2) is **not robust to a stronger equal-resource buffered/staged operand-service baseline**. With the same three single-port banks and two-completion cap, independently verified feasible four-cycle schedules exist for both baseline and candidate: **4 vs 4, 1.000x**. The previous 6 vs 4 atomic-mask result remains mathematically correct only under the restrictive same-cycle multi-bank-read assumption. This is a model-fidelity falsification, not a GPU hardware result.

## Provenance

The staging prediction and independent-check requirements were committed first at [49210ae](https://github.com/sushxnthd/vektor/commit/49210ae71eaf622a287d2e322a9be8c004864033), before [the executable witnesses](test_staged_bank_service.py) at [5600d79](https://github.com/sushxnthd/vektor/commit/5600d798578803664e036003ff52aab9a986fe2b). A second, analytically motivated bank-B bottleneck protocol was frozen at [62d8a22](https://github.com/sushxnthd/vektor/commit/62d8a22f943fb346d082d7ba07cc3219041aad34), before [the boundary/transfer checker](test_staged_bank_boundary.py) at [99fb1a6](https://github.com/sushxnthd/vektor/commit/99fb1a61c2baa14479ac9c901527ddde285b7f1d). This follow-up was designed after inspecting the atomic-model result; it is **not** an independent real-workload holdout.

## Equal-resource comparison and exact witnessed cases

Each instruction requests reads from bank A, B, or C. Baseline masks AB/BC/CA; hypothetical candidate A/BC/CA. One read per bank per cycle, no duplicate reads, up to two newly completed instructions per cycle, arbitrary staging of different operands across cycles, all instructions ready, unlimited in-flight buffers. The independent validator checks every labeled operand exactly once, each bank's per-cycle occupancy and completion cap. An attained capacity lower bound proves optimality *for the listed witnesses*, not for all GPU schedules.

| Workload (a,b,c) | Atomic baseline/candidate | Staged baseline/candidate | Staged gain |
|---|---|---|---|
| Original predicted atomic win (2,2,2) | 6 / 4 | **4 / 4** | **1.000x** |
| Original no-win (0,3,3) | 6 / 6 | **6 / 6** | 1.000x |
| Prior transfer (2,1,3) | 6 / 5 | **5 / 5** | 1.000x |
| Newly frozen bank-B-limited win (2,2,0) | 4 / 2 | **4 / 2** | **2.000x** |
| Newly frozen count transfer (2,1,0) | 3 / 2 | **3 / 2** | **1.500x** |

These are **idealized finite-workload service-cycle ratios**, not measured instruction throughput, GPU IPC or physical speedups. The win cases remain hypothetical: no mechanism for eliminating the B-bank read is demonstrated.

## Compact conditional capacity boundary

For a=n_AB, b=n_BC, c=n_CA, N=a+b+c, define U=max(ceil(N/2),a+c,b+c). Under ideal staged bank service, lower bounds are

    L_base = max(U, a+b)
    L_cand = max(U, b)
    G_capacity = L_base / L_cand

The envelope predicts an improvement **if and only if** the baseline B-bank demand a+b strictly exceeds U (for nonnegative integer a,b,c). An independent 0..5 count sweep checks this algebraic boundary. The bound is *not* a universal achieved throughput law: bounded collectors, issue/dependency timing, register-cache hits, control, and clock degradation can invalidate equality with the lower bound. For the five listed cases, independently checked schedules attain both bounds, so the cycle counts are exact within the stated model.

## Falsification and next decision

The old atomic-only 1.500x gain cannot justify promoting read elimination. A stronger staged baseline removes it in the original predicted-win regime. The new bank-B-limited synthetic cases show why the proper research question is **whether actual workloads are bank-B critical even after operand staging, compiler scheduling and cache reuse**, and whether any new physical mechanism can reduce those reads more cheaply than established reuse-aware collectors or rematerialization.

Do **not** promote the hypothetical read-elimination mechanism, claim novelty, or infer GPU throughput. Before a new architecture: provenance-verified compiled SASS, dynamic execution and bank mapping, bounded collector/reuse controls, a matched-resource baseline, then RTL equivalence, synthesis, timing/electrical checks and workload-level evaluation. Prior V287/V296 history remains historical. V317 is an evidence/falsification branch, not a physical GPU mechanism.
