# V317 functional-information kill test: unqualified B-read deletion is not a GPU mechanism (2026-11-01)

**Decision:** reject the current hypothetical `AB -> A` B-read deletion as a physically credible architecture candidate. Preserve the V317 SASS and scheduling instruments on the existing branch/PR. Do not promote another mechanism without a real equivalent dataflow and equal-resource comparator.

## Prospective provenance and scope

The [functional-information protocol](FROZEN_FUNCTIONAL_INFORMATION_GATE_20261101.md) was committed as `a1a4d9a` **before** the new semantic checker, tests or outcomes. The [exhaustive checker](functional_information_gate.py) and [independent two-world tests](test_functional_information_gate.py) implement that protocol. Reproduce from repository root:

```sh
python -m unittest research.v317.test_functional_information_gate -v
python -m research.v317.functional_information_gate > functional_information_gate.json
```

The V317 hosted audit workflow runs the new tests and archives source-pinned JSON. This is **four-bit toy-program semantics**, not GPU RTL, SASS dynamic trace evidence, or physical performance.

## Decisive information-theoretic counterexample

Define `AB(A,B)=(A+3B) mod 16` and `BC(B,C)=B xor C`. The prior service-cycle model simply removed AB's B operand without providing another source for its value. With `A=0,C=0`, worlds `B=0` and `B=1` have **identical remaining visible inputs** but require AB outputs 0 and 3. Any deterministic A-only implementation must return the same result in both worlds. It cannot be functionally equivalent.

The checker enumerates all 4,096 triples (A,B,C). Direct deletion fails **3,840/4,096**. The independent two-world proof establishes impossibility for this arbitrary-B interface; exhaustive testing is an additional regression, not a substitute for proof.

## Valid repairs and strongest same-knowledge baseline

| Repair, with its explicit proof condition | Exhaustive passing cases | Candidate physical transactions in toy model | Equally informed baseline | Incremental candidate transaction advantage |
|---|---:|---|---|---:|
| B is provably A; use A | 256/256 | B reads 0 | Same compiler rewrite | 0 |
| B is provably A xor C; recompute | 256/256 | B reads 0; C reads 1; XOR operations 1 | Same rematerialization | 0 |
| AB and BC consume the same architectural B identity; forward BC's B | 4,096/4,096 | Shared B reads 1; C reads 1; forwarded values 1 | Same legal reuse path | 0 |

A different register identity is rejected even if one observed numerical value coincides (4,096/4,096 adversarial admissions rejected). No additional B read may be silently removed by borrowing BC's source without accounting for the BC read and the forwarding path. The compiler controls assume that the baseline receives **the same proof/identity information** as the candidate; this is the strongest fair comparator for the explicitly modeled transformations.

These are **abstract transaction counts**, not equal-area physical implementations. Actual forwarding crossbars, wire loading, RF cache behavior, extra C-bank pressure, recomputation latency, power, and clock penalties are unmeasured. The 0 incremental transaction advantage does not prove that every conceivable future hardware optimization has zero benefit; it falsifies the presently proposed mechanism and these specific repairs as a unique architecture advantage.

## Consequence for earlier V317 results

The 2.000x and 1.600x figures in [operand-identity reuse service study](OPERAND_IDENTITY_REUSE_STRONG_BASELINE_RESULT_20261101.md) describe a *hypothetical service system that no longer has to supply a required B value*. They are **not feasible end-to-end GPU speedups**. Any future positive result must show a concrete equivalent operand-supply mechanism, independently check semantic correctness, and include all ports, data movement, timing, power and area against a compiler/collector baseline that can use the same information.

**Next science gate:** choose an actual RTL-implementable source of saved reads (not an unqualified deleted input) and freeze one physical predicted-win and one no-win regime before implementation. If no implementable path or independent dynamic register-demand evidence exists, do not promote a new mechanism. V317 remains a measurement/falsification workstream. No RTX 5090 equivalence is claimed.
