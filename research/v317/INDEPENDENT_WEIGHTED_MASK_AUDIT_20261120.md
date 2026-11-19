# Independent weighted protected-service audit — 2026-11-20

Branch: `research/v317-sass-provenance-gate`; draft PR #34. Active lineage V296/V317; V287 historical only.

## Method
Independently reimplement the four-request, four-bank, two-reads/request, two-ports/bank combinational audit using 16 subset bitmasks, direct port-count feasibility and scan-order greedy. The protected oracle is constrained to include request zero. Exhaustively enumerate all 4^8 = 65,536 ordered operand assignments. Apply integer weight h^k where k is the number of bank-zero operands; h in {1,2,3,5}. Independent checker: `rtl/independent_weighted_mask_audit_20261120.py`.

## Reproduced exact results
| h | Greedy weighted grants | Protected weighted grants | Ratio |
|---|---:|---:|---:|
| 1 | 171076 | 173572 | 1.014590 |
| 2 | 963271 | 976891 | 1.014139 |
| 3 | 3772044 | 3818364 | 1.012280 |
| 5 | 31796356 | 32049412 | 1.007959 |

Unweighted joint histogram (greedy, protected): (1,1): 1468; (2,2): 22620; (2,3): 2496; (3,3): 36432; (4,4): 2520. Thus only 2496/65536 assignments (3.8086%) admit a strict protected cardinality improvement, always exactly one extra grant in this enumeration. Both implementations independently pass exact integer assertions.

## Decision and limitations
The zero-cost oldest-protected combinational oracle stays below the preexisting 1.02x materiality threshold in every evaluated weighted distribution. This is a negative ceiling under the specified synthetic model, not a universal architecture impossibility. It does not validate bounded lifetime fairness, stateful queue throughput, workload holdouts, or physical implementation. Existing compact-greedy area dominance and electrically illegal routes remain blockers. Do not claim GPU IPC, power, RTX 5090 equivalence or a deployable scheduler. Next meaningful investment must prioritize realizable stateful fairness plus equal-resource electrically legal physical evidence; otherwise kill the candidate.
