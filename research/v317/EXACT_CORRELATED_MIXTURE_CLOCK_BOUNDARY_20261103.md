# Exact correlated-bank mixture clock boundary (2026-11-03)

## Correction to earlier optimistic upper bound

The previous V317 correlation sensitivity used U=(1+q P(E))/(1+d), a **valid but loose optimistic upper bound**, not the exact net gain. The exact restricted two-cycle model also has an independently enumerated greedy expectation G(B), and the correlated component changes that denominator. Under the explicit mixture in which an entire eight-operand batch is iid-uniform with probability q, otherwise all operands map to the same bank, the concentrated case yields exactly two completions for both policies (two read ports/bank and two cycles).

With P(B) and G(B) from the independently verified partition polynomials:

```
P(B)=[153(B)3+212(B)4+61(B)5+4(B)6]/B^8
G(B)=[2(B)1+404(B)2+3511(B)3+6536(B)4+
      4139(B)5+1060(B)6+112(B)7+4(B)8]/B^8
R_exact(B,q,d)=[1+q P(B)/(q G(B)+2(1-q))]/(1+d).
```

This follows from the law of total expectation; the oracle gains exactly one completion on event E in the iid component and zero in the concentrated component. For clock penalty d, a strict win requires q[P(B)-d(G(B)-2)] > 2d. If the bracket is nonpositive, no q in [0,1] can win; otherwise q > 2d/[P(B)-d(G(B)-2)]. This corrects the earlier necessary q>d/P(B) (which remains a weaker necessary bound).

## Exact rational sensitivity, illustrative d=0.005

| B | q=0.25 net | q=1 net |
|---:|---:|---:|
| 4 | 1.008661324 | 1.030459773 |
| 8 | 1.000385539 | 1.008556232 |
| 12 | 0.997619151 | 1.001538186 |
| 16 | 0.996528747 | 0.998793513 |
| 32 | 0.995411579 | 0.995992204 |
| 48 | 0.995197510 | 0.995456575 |
| 64 | 0.995122102 | 0.995267977 |

**Boundary sensitivity:** 8-bank q=0.25 barely survives the illustrative clock penalty; 12-bank q=0.25 does not. At 16 banks, even the iid oracle loses. These are exact conditional calculations for a synthetic *batch* oracle, not measured RTL delay, dynamic GPU throughput, power, or hardware feasibility. Correlated workloads outside this two-component mixture are not identified by q. No new scheduler is promoted. Prior electrically illegal routes and compact-greedy area dominance remain binding.

Reproduce: `python research/v317/exact_correlated_mixture_boundary.py`. The independent checker requirement for the full GPU mechanism is still unmet; the script is rational-arithmetic verification of the formula, not an independent RTL audit.
