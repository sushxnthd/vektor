# V317 operand-identity reuse challenge: frozen before evaluating new holdouts (2026-11-01)

**Scope.** Continue the single existing V317 falsification branch and draft PR #34. No new hardware mechanism is promoted. The previously derived two-class collector law assumes that each AB and BC instruction requires an independent B-bank read. This protocol challenges that assumption against a stronger *equal-resource* baseline that can share a read of the **same register value** across two collectors. This is an idealized multicast/reuse capability, not evidence that any particular NVIDIA GPU provides it for these instructions.

## Frozen question and mechanism

Does the hypothetical AB->A read-elimination candidate retain a material service-cycle gain if the baseline is allowed to broadcast one B-bank read to a simultaneously serviced AB and BC instruction when both refer to the **identical** B source-register identity?

There are a AB and b BC instructions, initially ready. Exactly s disjoint AB/BC pairs (0 <= s <= min(a,b)) share a B source identity. Every other B identity is unique. A and C reads remain unshared. One read port per A/B/C bank, at most two completions per cycle, and K collector slots in **both** systems. Within one cycle, a read of a B identity may supply both members of its single paired identity, if both are admitted. The candidate still hypothetically deletes B from AB, without any functional equivalence claim. Both systems receive the same multicast/reuse path and physical resource limits. No hidden free extra port.

The baseline is allowed arbitrary staged reads and optimal scheduling. Any proof must show why staging cannot beat the proposed lower bound, not merely solve an artificially weaker atomic-issue baseline. Compare the exact analytic lower bound with an independent graph-matching / exhaustive set-partition oracle and explicit legal schedule witnesses. Do not use the candidate law to generate oracle decisions.

## Frozen predictions (service cycles, not GPU IPC)

For nonempty N=a+b and K=1: baseline=candidate=N. For K>=2:

- Baseline T0 = a+b-s (B port must read N-s distinct values; this bound is attained by servicing s shared pairs and all unmatched instructions).
- Candidate T1 = max(a,b) (A port requires a cycles; B/C ports require b cycles; pair unlike classes to attain).
- Gain G = (a+b-s)/max(a,b).

Predeclared tests, to be checked only **after** this protocol commit:
1. Predicted win: (a,b,s,K)=(3,3,0,2), T0/T1=6/3=2.000.
2. Predicted no-win: (3,3,3,2), T0/T1=3/3=1.000.
3. Partial reuse: (4,3,2,2), T0/T1=5/4=1.250.
4. Tight occupancy: (2,2,2,1), T0/T1=4/4=1.000.
5. Unseen count transfer A: (5,4,1,2), T0/T1=8/5=1.600.
6. Unseen count transfer B: (2,5,2,3), T0/T1=5/5=1.000.

Exhaustively check a,b in 0..4, N>0, all valid s, K in {1,2,3}; report number of configurations and any discrepancies. A separate exhaustive partition oracle must check small labeled instances independently of the analytic law and of the graph matcher. A legal schedule witness must obey K, bank ports, issue width, and same-value identity for shared B reads. Include a deliberate false-sharing adversarial case with unequal B identities and assert rejection.

## Materiality and physicality gate

At K>=2, materiality >1.02 requires (a+b-s)/(max(a,b)+C)/(1+delta)>1.02, where C is additional service-equivalent control cost and delta is relative cycle-time penalty. This is a **conditional bound**, not measured C or delta. If the baseline already exploits B identity reuse, the previous s=0 law overstates benefit. Real SASS register identities, dynamic reuse, actual register-cache behavior, wire/fanout cost, equal-area RTL and timing remain unknown. Do not claim measured GPU speedup, a new physical mechanism, or RTX 5090 equivalence. Kill the hypothetical candidate if a strong compiler/cache/collector baseline erases it.
