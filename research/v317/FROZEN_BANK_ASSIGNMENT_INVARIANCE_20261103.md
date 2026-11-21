# Frozen V317 physical-bank assignment identifiability test (2026-11-03)

## Scientific question
Can the exact two-cycle head-preserving scheduling opportunity from V317 be identified from **register-source identity alone**, without the unpublished physical register-bank mapping? This is a *falsification of workload attribution*, not a new GPU architecture or measured throughput. Preserve the existing V317 branch/PR and earlier physical kills.

## Scope and fixed model
Four ordered valid requests, exactly two source-register tokens per request, two reads/bank/cycle, issue cap two, two cycles, no arrivals, no register-cache/reuse-cache modeling, and oldest-request preservation in each cycle. A bank assignment maps each distinct source-register token to one bank consistently across all requests. The mapping is otherwise unconstrained and is **not asserted to match any NVIDIA architecture**. The only target outcome is the previously proved per-batch oracle-minus-greedy event E in {0,1}. Physical bank mapping, dynamic SASS frequency, actual operand reads, RTL PPA and GPU IPC are unknown.

## Precommitted tests and predicted outcomes
1. Exhaust all restricted-growth set partitions of the distinct source tokens, assigning at most B bank classes. For B >= number of distinct tokens, this exactly covers **all physical-bank assignments up to bank-label permutation**. Assert 4,140 partitions for eight distinct tokens at B=16 (Bell(8)).
2. On the unseen eight-distinct-token request pattern `((0,1),(2,3),(4,5),(6,7))`, predict E is **not identifiable**: both E=0 and E=1 occur under legal assignments.
3. On the all-identical pattern `((0,0),(0,0),(0,0),(0,0))`, predict E=0 under every assignment.
4. On `((0,0),(1,1),(2,2),(3,3))`, predict E=0 under every assignment (may fail; retain any falsification).
5. On `((0,1),(0,2),(3,4),(3,5))`, predict either a nontrivial ambiguity or a structural no-win; report which without post-hoc relabeling.
6. Compare B=2,4,16, including whether the result changes when banks are constrained. Add an independent checker with a different event computation and brute-force labeled assignments for small m and B, with no evaluator imports.
7. Include at least one repeated-register sensitivity and one register-label permutation test. Do not conflate lexical SASS tokens with measured RF reads; register allocation, compiler reuse, unknown opcodes and dynamic execution remain unobserved.

## Decision rule
If an identity-only trace admits both E=0 and E=1, the trace cannot support a point prediction of this scheduling gain without a measured/verified bank map. If all mappings yield E=0, retain a **conditional no-win certificate for the stated bank-port model**. Do not promote any controller without a measured bank map, actual dynamic GPU workload traces, matched electrically legal RTL and a material tile-level benefit.

## Reproduction plan
Commit this protocol **before** running the new evaluator. Then commit a pure-Python partition enumerator, independent audit, raw JSON and report on the same persistent branch, updating draft PR #34. Use only local CPU resources.