# V296 equal-budget area-reinvestment staircase: exact prospective falsification (2026-10-26)

**Decision: the 5.6713% balanced-return mapped slice-area advantage does not create any extra slice under a one-slice or sixteen-slice equal-area budget.** This is a bounded, exact mathematical result about *already measured mapped standard-cell areas*, not an achieved GPU speedup, novel architecture, feasible layout, power measurement, or routed multi-slice tile. The physical post-route experiment remains an independent mandatory gate.

## Evidence and provenance

The prospective [frozen protocol](AREA_REINVESTMENT_STAIRCASE_PREREG_20261026.md) was committed first at `f8f0c326`. The [executable independent-check experiment](area_reinvestment_staircase.py) was committed next at `0970be0d`, then its [frozen machine-readable results](AREA_REINVESTMENT_STAIRCASE_RESULTS_20261026.json) at `2252e147`. The inputs are the hosted Nangate45/Yosys 0.9 balanced-return four-way mapped audit from Actions run 40244774412, artifact 12618038449: V296 9286.592 um², optimized serial 9844.926 um². The prior SHA-pinned audit and original RTL/physical artifacts remain unchanged. The matched balanced-return physical jobs were still running at the initial inspection of this experiment.

## Exact predictive boundary and falsification

At a fixed total budget of `H + N*A_serial`, where `H` is identical shared fixed overhead and the remaining area must pay for *complete independent* slices, the optimistic number of pairwise copies is

`n_pairwise(N) = floor(N*A_serial/A_pairwise)`, versus `n_serial(N)=N`.

The **first** possible extra candidate copy is at

`N_min = ceil(A_pairwise/(A_serial-A_pairwise)) = 17`.

This is a discrete **area-reinvestment staircase**. A smaller mapped slice does not automatically make one single slice faster or more productive. An independently implemented enumeration of all copy counts for N=1..1000 exactly matched the formula; just-below/at-threshold and equal/worse-area negative controls passed. All calculations use exact rational arithmetic, not rounded floating-point copy counts.

| Frozen budget / shared bandwidth | Serial slices | V296 slices, ideal packing | Predicted useful gain |
|---|---:|---:|---:|
| 1 serial slice / 100 GB/s | 1 | 1 | **0%** |
| 16 serial slices / 100 GB/s | 16 | 16 | **0%** |
| 17 serial slices / 100 GB/s | 17 | 18 | **+5.88235% conditional** |
| 17 serial slices / 10 GB/s | 17 | 18 | **0%** |

For this *synthetic model only*, the same verified i.i.d bank-admission expectation `q=957548877/320000000` is applied to each independent slice, with a common **assumed** 3.5 ns feasible clock, 4 bytes/admission and no control overhead. The frozen throughput law is

`R_i = min[n_i*q*f_i/(1+h_i), W/b]`.

Because both arbiters have formally equivalent grant semantics, no same-clock single-slice issue-throughput advantage exists. The 17-to-18-copy scenario is **only** a conditional resource-packing thought experiment. The 10 GB/s shared bandwidth cap erases the hypothetical advantage. No actual physical multi-slice design, memory system, 17/18-way RF implementation, feasible 3.5 ns balanced-return clocks, or bandwidth capacity was demonstrated.

## Robustness of the discrete boundary

| Adverse mapped-area perturbation | Earliest extra copy |
|---|---:|
| No perturbation | 17 serial copies |
| V296 area +2%; serial area -2% | **54** serial copies |
| V296 area +5%; serial area -5% | **No finite threshold** |

The threshold is discontinuously sensitive to small differences in actual area. A shared fixed overhead `H` cancels *only* when both candidates receive the same reserved `H` budget. Independent routing, buffer repair, congestion, replicated interconnect, register-file macros, clock distribution, thermal/power limits, scheduling coordination, and area fragmentation can all prevent the ideal copy count. These are not PVT measurements or a license to assume area can be reinvested for free.

## Independent checking and scientific decision

Local execution of `python3 research/v296/area_reinvestment_staircase.py --self-test` passed 1000 independent additive copy-count enumerations, the exact frozen win/no-win regimes, equal/worse-area controls, adverse area sensitivities, bandwidth caps, and invalid inputs. This was **local**, not hosted CI; no new hosted validation is claimed. The experiment does not open existing prospective GPU workload holdouts.

**No architecture-speedup claim is supported by this experiment.** It falsifies the inference that a 5.67% mapped-area reduction automatically increases the throughput of a single equal-resource tile. The only conditional positive consequence requires demonstrably feasible extra complete slices at equal total consumed silicon and available workload/bandwidth. The immediate V296 physical gate is still matched detailed-route OpenRCX setup/hold/cap/slew at the frozen 3.5 ns; the strongest independently optimized serial control receives the same RF-return repair. If either physical implementation fails, reject integrated speedup claims regardless of this optimistic packing calculation.

V296 remains the sole provisional architecture mechanism; V287 stays retired. PR #13 remains draft and unmerged. Kernellum PR #119 and its prospective holdouts are unchanged. No RTX-5090-equivalence, production GPU, measured power or energy advantage is claimed.
