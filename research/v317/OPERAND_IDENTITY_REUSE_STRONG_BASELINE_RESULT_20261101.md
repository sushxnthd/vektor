# V317: operand-identity reuse collapses the previous two-class gain in a strong baseline (2026-11-01)

**Decision:** retain V317 as a falsification/evidence instrument; do not promote hypothetical AB B-read deletion. The previously validated two-class law was conditional on **independent** B reads. An equally ported baseline with same-value operand multicast can match the candidate exactly in a frozen no-win regime. This is an exact synthetic service-cycle result, **not** a GPU architecture improvement.

## Prospective provenance

- The new [identity-reuse protocol](FROZEN_OPERAND_IDENTITY_REUSE_CHALLENGE_20261101.md) was committed first at [63f7a1b](https://github.com/sushxnthd/vektor/commit/63f7a1b73f0561fffe6696fb84ead7d20270ba2c), before implementing the new matching oracle or evaluating the specified new holdouts.
- Labeled-register [matching oracle](operand_identity_reuse.py), [independent exhaustive set-partition oracle and adversarial tests](test_operand_identity_reuse.py), and [source-pinned JSON generator](operand_identity_reuse_evidence.py) were committed subsequently.
- Local execution: `python -m unittest research.v317.test_operand_identity_reuse -v` (5 tests passed); `python -m research.v317.operand_identity_reuse_evidence > identity.json` (162 configurations, 294 independent partition checks, zero mismatches). The hosted workflow independently reruns the tests and archives source-pinned evidence; do not claim it passed until the actual run finishes.

## Stronger matched service baseline

Two instruction classes: AB and BC. There are a AB and b BC instructions, with s disjoint AB/BC pairs reading the **same B register value**. All other B identities are unique. Each instruction is ready. A/B/C each have one physical read port, completion width is two, and both designs have the same K collector slots. A B read may be multicast to two admitted instructions **only if its register identity is equal**. Candidate AB->A read elimination remains hypothetical and unimplemented. Both systems have identical service resources and reuse eligibility in the abstract model.

The matching oracle schedules legal same-cycle operand reads and completion. The independent set-partition oracle checks optimality on small labeled cases. Importantly, allowing arbitrary staged reads cannot beat the analytic B-port lower bound for the baseline: it must read a+b-s distinct B values, each using the single B port for one cycle. A schedule of s shared AB/BC pairs followed by unpaired instructions attains this bound with K>=2. Candidate requires at least a A-bank service cycles and b B/C service cycles, attained by pairing unlike classes. Thus the atomic schedules are already optimal even against a staged-read baseline **within this restricted identity model**.

## Frozen and unseen results

| Regime (a,b,s,K) | Baseline cycles | Candidate cycles | Ideal gain |
|---|---:|---:|---:|
| Predicted win (3,3,0,2) | 6 | 3 | 2.000x |
| Predicted no-win (3,3,3,2) | 3 | 3 | **1.000x** |
| Partial reuse (4,3,2,2) | 5 | 4 | 1.250x |
| Tight occupancy (2,2,2,1) | 4 | 4 | 1.000x |
| Unseen count transfer A (5,4,1,2) | 8 | 5 | 1.600x |
| Unseen count transfer B (2,5,2,3) | 5 | 5 | **1.000x** |

The exact law for N=a+b>0 is:

```text
K=1:  T0=N,       T1=N,        G=1
K>=2: T0=N-s,     T1=max(a,b), G=(N-s)/max(a,b)
```

For balanced a=b=m, define the fraction of matchable same-B pairs r=s/m. Then `G=2-r` (K>=2). At full identity reuse r=1, the candidate has **no incremental advantage**. This is a new *conditional reuse-sensitive boundary for this toy model*, not a novel physical law or evidence of GPU register-cache behavior.

The prospective six cases passed. A complete a,b=0..4, s=0..min(a,b), K=1..3 sweep checked **162** configurations with zero law discrepancies; **294** additional small-instance candidate/baseline checks agreed with an independently coded exhaustive set-partition oracle. An adversarial false-sharing witness using different B register identities was correctly rejected.

## Physical and novelty limits

The earlier s=0 gain of 2.000x is *not robust to identity reuse*. An implementation cannot simply remove B from AB without a functional equivalence mechanism. Conversely, same-value B multicast is not automatically free: fanout, read-data routing, collector wiring, cache policy, and clock penalties require RTL and synthesis before the baseline is physically matched. This experiment does **not** establish that modern NVIDIA GPUs have the modeled multicast behavior. The actual B-register identities, dynamic hit/reuse rates, and physical bank mappings are unknown.

For extra candidate control-equivalent service cost C>=0 and relative cycle-time penalty delta>=0, a material >1.02x gain in this model requires:

```text
K>=2 and (a+b-s) > 1.02 * (max(a,b)+C) * (1+delta).
```

At K=1 or full matching reuse (a=b=s), no positive candidate overhead can satisfy the threshold. The prior two-class law must now be explicitly labeled **zero cross-instruction B-identity sharing**; its result is not a general register-pressure prediction.

## Next decisive gate

Do not spend another run on abstract service-law elaboration alone. Obtain provenance-verified compiled SASS, dynamic operand identities, reuse/cache behavior, and an implementable, functionally equivalent read-avoidance path. Then compare against a reuse-aware compiler/collector baseline with matched RTL, port/wire load, timing and area. If strong equal-resource controls or timing penalties erase the gain, kill the mechanism. No new hardware architecture has been promoted, and no RTX 5090 equivalence is claimed.
