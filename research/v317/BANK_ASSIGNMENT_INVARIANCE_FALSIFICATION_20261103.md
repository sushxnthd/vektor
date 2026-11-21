# V317: bank-assignment identifiability and conditional no-win certificates (2026-11-03)

**Evidence tier:** exact symbolic bank-assignment enumeration and independent local audit. **NOT** observed NVIDIA bank mapping, measured RF reads, GPU workload IPC, RTL PPA or electrical signoff. The previously failed V317 integrated area/electrical gates remain binding; this does not promote a new controller.

## Frozen experiment and result
The [pre-outcome protocol](FROZEN_BANK_ASSIGNMENT_INVARIANCE_20261103.md) was committed as `d7dab0a` before the evaluator was run. Model: four ordered valid requests, two register-source tokens each, two reads/bank/cycle, K=2, two cycles, oldest-request preservation and no arrivals. A single unknown mapping assigns each *distinct register token* to one bank, consistently across the four requests. No actual GPU bank map or RF cache behavior is inferred.

**Precommitted predictions:** eight distinct registers admit both E=0 and E=1 at B=16 (**PASS**); all-identical registers always E=0 (**PASS**); four doubled registers always E=0 (**FAIL**, preserved). The latter pattern admits E=1 under one of 15 unlabeled four-bank partitions. An uncertain bank map cannot justify a positive point estimate.

| Register identity pattern | B=2 opportunity | B=4 iid-map oracle/greedy | B=16 iid-map oracle/greedy | B=16 map-invariant E |
|---|---|---:|---:|---|
| Eight distinct sources | none | 1.035612x | 1.003787x | ambiguous |
| Four distinct doubled sources | none | 1.025424x | 1.013034x | ambiguous; frozen no-win prediction **failed** |
| Shared sources `(0,1),(0,2),(3,4),(3,5)` | none | 1.051211x | 1.026366x | ambiguous |
| All identical | none | 1.000000x | 1.000000x | guaranteed no-win |
| Two alternating source pairs | none | 1.000000x | 1.000000x | guaranteed no-win |
| Cross-repeated source pairs | none | 1.000000x | 1.000000x | guaranteed no-win |

These ratios are **optimistic exact two-cycle oracle ratios under an invented iid uniform bank-assignment null**, not measured throughput or hardware speedups. The oracle can have unbounded controller cost and the bank mapping need not be random.

## Exact predictive identity and identifiability boundary
Let `m` be the number of distinct source tokens in a four-request batch. Each partition `pi` of those tokens into `k<=B` nonempty blocks represents `(B)_k=B!/(B-k)!` labeled bank maps. Define `E(pi)` as the exact oracle-minus-greedy completion event, which is either zero or one. Under an **explicit iid uniform mapping assumption**,

```
Pr_B(E=1) = [sum_{pi, |pi|<=B} (B)_{|pi|} E(pi)] / B^m
R_B = 1 + Pr_B(E=1) / E_B[G]
```

The sum is exact, not Monte Carlo. The eight-distinct, B=16 case has 4,140 unlabeled partitions (Bell(8)); 430 admit E=1, but weighted event probability is only `2025345/134217728 = 0.015090`, yielding 1.003787x. For B=4, 365 of 2,795 partitions admit E=1, with weighted probability `1095/8192 = 0.133667`.

A **mapping-invariant no-win certificate** exists iff every admissible partition has E=0. If both outcomes occur, identity alone cannot identify whether the oracle improves that batch. A single observed bank assignment would resolve this particular combinational uncertainty, but dynamic execution, RF-cache hits, control timing and physical costs would still remain unmeasured.

### General B=2 theorem (restricted model)
For *any* four two-source requests, two banks with two reads/bank and K=2 imply E=0. Each request has bank profile (2,0), (1,1), or (0,2). Two requests can coissue only if their profiles complement. All compatible partners of a fixed head therefore have the same profile. Swapping the head's partner cannot change whether the two remaining profiles complement, so it cannot improve two-cycle completions. This is **not** a general theorem about multi-cycle queues, caching, or real GPU operand collectors.

## Independent verification
The evaluator uses restricted-growth partition strings. The independent checker instead constructs set partitions by recursive block insertion, recomputes two-cycle service by enumerating legal issue sets, and verifies weighted counts against direct labeled-bank enumeration. **Local independent audit passed**: 7,570 unlabeled partition cases, 201,866 directly enumerated labeled bank maps, 6,561 bank-label permutations and 18 register-renaming invariance checks. The failed four-doubled prediction was explicitly checked as a falsification. Hosted workflow is committed; hosted success is not asserted here.

Reproduce:
```sh
python3 research/v317/rtl/bank_assignment_invariance.py > /tmp/v317-bankmap.json
python3 research/v317/rtl/audit_bank_assignment_invariance.py /tmp/v317-bankmap.json
```

Evaluator: [bank_assignment_invariance.py](rtl/bank_assignment_invariance.py). Independent audit: [audit_bank_assignment_invariance.py](rtl/audit_bank_assignment_invariance.py). Hosted workflow: [v317-bank-assignment-invariance.yml](../../.github/workflows/v317-bank-assignment-invariance.yml).

## Architecture decision
**No mechanism promoted.** This closes a specific inference loophole: lexical register-source identities plus a hypothesized number of banks do not generally identify a scheduling benefit. The exact conditional no-win certificates are useful negative controls, not a GPU performance breakthrough. Repeated lexical operands may be satisfied by register reuse/cache mechanisms; unknown dynamic SASS frequencies and compiler physical register allocation can invalidate the simple read-demand proxy.

The next eligible experiment must obtain provenance-pinned compiled GPU kernel disassembly and independently supported bank/reuse assumptions, then freeze a workload-derived predicted-win/no-win test. Any surviving candidate still needs an equal-resource RF-cache-aware controller, sustained finite-buffer performance, matched routed area/timing, legal electrical checks, wire/load and power sensitivity, and a defensible integrated tile consequence. Preserve V317's existing physical falsification and do not claim RTX 5090 equivalence.
