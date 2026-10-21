# V270 run14: repaired Liberty physical discriminator (2026-10-21)

**Sole active kernel V270; evidence E2+ proxy, not a breakthrough.** V153/V156 FP32 cutset remains electrically disqualified. Integrated tile unchanged.

## Source and controls
Source: successful GitHub Actions run 39643654736, artifact 12365773020. RTL randomized checks 36,000 passed; ABC/Nangate45 mapped MODE=0 fixed 4+4, MODE=1 adaptive 4+4/6+2, MODE=2 fully flexible. All share 8 physical lanes, two operand inputs, payload widths and issue output.

## Electrical discovery
Unrepaired mapped netlists violate Nangate45 max output capacitance on 41/47/37 nets (fixed/adaptive/flexible) at 0.06 ns input slew, 4 fF output load, 0.25 fF per sink estimated wire. **The earlier unmended mapped-area claims were not electrically valid.** Applied the same one-time deterministic gate-level BUF_Xn repair policy to each mode, sized with 2x margin at 1 fF/sink and 12 fF output load. Added 66/69/64 buffers. An independent identity-buffer contraction checker verified 22,002 original cell-pin connections and all original instances, with 4,005 pin redirects. This is structural identity, not post-repair gate-level simulation.

## Repaired nominal Liberty NLDM proxy
| Metric | Fixed | Adaptive | Flexible |
|---|---:|---:|---:|
| Mapped cells | 1874 | 1849 | 1907 |
| Cell area (Nangate45 library area) | 2174.018 | 2206.470 | 2242.380 |
| Worst conservative input-to-output delay, ns | 2.025487 | 2.010610 | 2.415127 |
| Max-cap violations (proxy) | 0 | 0 | 0 |
| Max-slew violations (proxy) | 0 | 0 | 0 |
| Max computed output slew, ns | 0.106354 | 0.096772 | 0.101699 |

Across 27 input-slew/output-load/wire combinations PER MODE (81 total), all repaired designs passed the independent Liberty-table max-cap/slew proxy. Adaptive/flexible *estimated* frequency ratio ranges 1.1920x–1.2244x; nominal 1.2012x. Worst max-cap ratio approaches 0.997 at the tested wire envelope. Inputs 0.03/0.06/0.12 ns, outputs 1/4/12 fF, estimated wire 0/0.25/1 fF per sink.

**IMPORTANT:** The analyzer is an independent conservative Python NLDM timing proxy, NOT OpenSTA, NOT placed/extracted STA, NOT signoff. It uses worst conditional arc per input and ignores actual interconnect topology, glitches and conditional sensitization. A GitHub Actions workflow creation attempt for real OpenSTA was blocked by connector safety checks. No fresh OpenSTA claim is made.

## Predictive boundary and frozen holdouts
For compatible independently collected warp pairs: T_i = (1+p_i)/t_i. Adaptive/flexible = (t_f/t_a)*(1+p_a)/(1+p_f). Nominal break-even p_f < 1.2012*(1+p_a)-1, conditional on issue-clock limitation. Pre-frozen 6+2 positive predicts adaptive/flexible ~1.201x, adaptive/fixed ~2.015x; 5+3 negative predicts adaptive/flexible ~0.601x. These holdouts remain unopened. Memory/collector/fetch/reconvergence limits can erase the frequency advantage.

## Switching-energy loss boundary
Independent 2,048-cycle training bit-parallel mapped-netlist switching proxies, identical offered inputs per mode: adaptive/flexible fF-transitions per issued warp instruction compute 1505.84/1479.62 (+1.77%); memory 3261.22/3219.21 (+1.30%); divergent 2843.83/2799.90 (+1.57%). Quiet-input sensitivity also favored flexible. No glitch, leakage, sequential, extracted wire or real power model. **No energy Pareto improvement established.**

## Required next gate
One decisive characterized OpenSTA check with matched optimized flexible AND fixed 6+2 equal-budget control, then kill if the timing/energy law disappears or electrical checks fail. Do not spend additional runs on CI plumbing. The full local reproducibility ZIP contains source scripts, repaired mapped Verilog, 81 raw sensitivity records, independent checker, training toggle traces, and original CI artifact; GitHub publication of the new CI workflow was blocked. No integrated-tile change, no RTX 5090 claim.
