# V296 logical-switching stress test: activity proxy reverses under extreme bank hot spots

Date: 2026-10-28. Sole provisional mechanism: V296 pairwise arbitration. V287 retired. Research branch: research/v296-pairwise-bank-conflict. Draft PR: #13.

## Question and scope

Can V296's lower routed *area* be used to infer lower *dynamic power*? No. Before any such claim, test whether even a limited RTL-observed-value transition proxy maintains a consistent sign under different bank-overlap and temporal regimes.

This experiment is **not a physical-power measurement**, a synthesized gate-activity report, a power estimate, a new routed result, or GPU performance evidence. Observed logical vectors differ in width and structure between implementations, and ignore internal gate switching, glitches, clock tree, parasitics, actual capacitance, memory macros and voltage. Ratios below **must not** be interpreted as energy ratios or percentage power savings.

## Method

Reproducible script: [v296_logical_switching_proxy.py](v296_logical_switching_proxy.py).

- Independently implement the four-slot greedy two-read-port admission rules for pairwise equality/hit-count and strongest V295 serial one-hot accumulation.
- Check **104,976** structured exhaustive cases (16 validity masks times 3^8 bank assignments) for exactly matching admissions, plus mutation-style known cases.
- Generate four development and four distinct synthetic evaluation regimes with 40,000 cycles and two fixed seeds each (1701, 1709), 640,000 total cycle-pairs.
- For each representation, count Hamming transitions between *selected RTL-level observed vectors* on successive cycles. These are **not physically matched net lists**. Vary valid-request probability, bank-0 hotspot probability and temporal persistence.
- Report exact admission equality, admitted waves/cycle, same-bank operand frequency, observed transition counts and ratios. Do not fit a power law from this proxy.

## Results (two-seed averages)

| Synthetic regime | Observed pairwise / serial transitions | Admitted waves/cycle |
|---|---:|---:|
| Uniform sparse | 0.1211 | 1.3824 |
| Uniform dense | 0.1258 | 3.4623 |
| Hot-bank sparse | 0.5503 | 1.0313 |
| Hot-bank dense | 0.6625 | 1.7494 |
| Medium mixed | 0.2733 | 2.0247 |
| Extreme hot bank | **1.7180** | 1.0295 |
| Sticky temporal | 0.4391 | 2.0220 |
| Cold temporal | 0.4381 | 2.0231 |

Every pairwise/serial admission result agreed. The extreme-hot case reverses the *chosen logical-vector transition-count ordering*, despite the previously measured routed-area ordering. The ratio is **not** evidence that V296 consumes 1.718 times the serial power. The observed vectors have different physical meanings, and the experiment cannot determine their capacitance or glitch activity.

The regime labels were defined as development versus synthetic evaluation regimes, but the latter were not independently sealed prospective holdouts. No prospective validation or novel power law is claimed.

## Independent architectural boundary

With identical admission sequences, identical frequency, identical occupancy and identical latency, V296 cannot deliver additional issue throughput from arbitration alone. At equal useful work rate, an energy-per-wave advantage requires **P_V296 < P_serial**. More generally, with useful throughput T and total power P:

    E_V296 / E_serial = (P_V296 / P_serial) / (T_V296 / T_serial).

For the previously studied *hypothetical L1-to-L2 occupancy-limited comparison* (N=2, B=2, q=0.9), even assuming the fixed-path routed maximum D4 frequency increase of 1.004783x, the best synthetic throughput ratio is 0.528833. Thus energy per wave would improve only if candidate power were below 52.8833% of the hypothetical L1 reference. **This is not a matched V296-versus-serial power comparison** because both actual deferred-write contestants have L2.

## Decision

**Reject area-implies-power and activity-implies-power extrapolations.** Do not claim an energy improvement, even when the logical proxy favors pairwise. This test supplies a falsification of the proxy's *sign stability*, not a physical energy verdict. The next decisive step is matched routed completion of the D8 serial control, followed by gate-level VCD/SAIF activity and matched power estimation on completed designs under identical traces, voltage, frequency, memory model and constraints. If neither area packing nor matched power/energy establishes a real benefit, kill V296 rather than changing mechanism labels.

Existing D4 serial setup/hold failure, D8 serial timeout, 30,000 um² one-slice equality and prior negative evidence remain unchanged. No RTX 5090 equivalence is claimed.
