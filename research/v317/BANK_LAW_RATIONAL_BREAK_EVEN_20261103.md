# V317 rational break-even certificate (2026-11-03)

**Evidence tier:** analytical necessary-condition falsification; no RTL, route, power, GPU IPC, or actual bank mapping established.

The eight-operand uniform bank-assignment model gives P(E|B) = [153(B)_3 + 212(B)_4 + 61(B)_5 + 4(B)_6]/B^8. In the *explicitly specified* mixture model, a fraction q of assignments are independent-uniform and the remainder map all operands to one bank, so P_mix(E)=q P(E|B). This scaling is **not** valid for arbitrary correlated mappings.

If each batch can gain at most one completion and the baseline completes at least one, an optimistic throughput upper bound with clock-period penalty d is U(B,q,d)=(1+q P(E|B))/(1+d). Thus **q > d/P(E|B)** is necessary for positive net gain. It is not sufficient; actual baseline completion denominator, traffic, ports, occupancy, wire delay and energy can tighten the decision. Different source distributions or temporal queue states require new proofs.

At illustrative d=0.005, rational evaluation yields:

| Banks | P(E) | Minimum q necessary | Upper net at q=0.25 | Upper net at q=1 |
|---:|---:|---:|---:|---:|
| 4 | 0.133667 | 0.0374 | 1.028275 | 1.128027 |
| 8 | 0.053533 | 0.0934 | 1.008341 | 1.048291 |
| 12 | 0.025999 | 0.1923 | 1.001492 | 1.020894 |
| 16 | 0.015090 | 0.3313 | 0.998779 | 1.010040 |
| 32 | 0.003885 | 1.2871 | 0.995991 | 0.998890 |
| 48 | 0.001735 | 2.8824 | 0.995456 | 0.996751 |
| 64 | 0.000977 | 5.1176 | 0.995268 | 0.995997 |

The certificate kills B>=32 even at q=1 for this clock penalty, and B=16 at q=0.25. These are conditional *model* kills, not universal GPU architecture kills. Independent Python reproduction: `python3 research/v317/bank_law_break_even_certificate.py`. Values were also cross-checked in an independent local Fraction calculation.

**Decision:** do not promote V317 exact scheduling; earlier physical/electrical failures remain binding. Before further architecture claims, pin executable kernel provenance and bank mappings, measure finite-queue throughput, and compare a matched-resource controller after placement/routing. No new mechanism or branch is authorized by this certificate.
