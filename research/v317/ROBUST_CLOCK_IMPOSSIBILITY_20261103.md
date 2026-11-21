# V317: Robust clock-penalty impossibility boundary (2026-11-03)

## Status and provenance
New exact-arithmetic sensitivity of the existing *restricted synthetic two-cycle oracle*. This does not rehabilitate the physically falsified V317 controller or promote another mechanism. Existing compact-greedy physical-area and electrical failures remain binding.

## Monotonicity and universal no-win certificate
With P(B) and G(B) as previously independently enumerated, the two-component bank-correlation model has
`R(q)=[1+qP/(2+q(G-2))]/(1+d)`, q in [0,1], d>=0.
Differentiation gives `dR/dq = 2P/[(1+d)(2+q(G-2))^2] >= 0`.
Thus the **best possible** member of this correlated mixture family is q=1, regardless of the unknown correlation fraction. A positive net win is possible for *some* q if and only if `d < P/G`. For a specified d with `P-d(G-2)>0`, the strict threshold is `q>2d/[P-d(G-2)]`; a threshold >=1 certifies no win over all q in [0,1]. If the denominator is nonpositive, no positive q can win.

## Exact-rational evaluated sensitivity
All numbers below are computed from rational partition polynomials, rounded only for display. The q threshold assumes illustrative d=0.005, not measured routed delay.

| Banks | Maximum tolerable fractional clock penalty P/G | Strict q threshold at 0.5% | Any q can win at 0.5%? |
|---:|---:|---:|:---|
| 4 | 3.561207% | >0.080064 | Yes |
| 8 | 1.359901% | >0.228050 | Yes |
| 12 | 0.654588% | >0.619582 | Yes |
| 16 | 0.378748% | >1.934571 | **No** |
| 32 | 0.097217% | undefined | **No** |
| 48 | 0.043386% | undefined | **No** |
| 64 | 0.024432% | undefined | **No** |

The no-win conclusion for B>=16 at 0.5% is **uniform over every q** in this explicitly defined mixture, including the independent iid limit. It is not uniform over arbitrary real GPU bank mappings or different queue/workload models.

## Decision and reproduction
This is a *clock sensitivity falsification*, not a hardware timing measurement. Reproduce with `python3 research/v317/robust_clock_impossibility.py` or pass a rational penalty such as `1/1000`. A real controller must beat compact greedy under equal-resource, electrically legal physical timing, and under workload-derived bank traces; otherwise kill the mechanism. No RTX 5090 equivalence, GPU IPC or SRAM-tile claim.
