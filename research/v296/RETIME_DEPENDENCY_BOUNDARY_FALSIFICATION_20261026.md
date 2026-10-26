# V296 operand-capture latency boundary and falsification (2026-10-26)

## Decision and evidence tier

**No GPU speedup established.** The retimed V296 tile-slice and its symmetric serial control have verified +1-cycle execution visibility but both fail the frozen 3.5 ns setup gate. The candidate's measured pre-CTS slack is -0.025959 ns (75.959 ps below the required +50 ps guard); the serial control is -0.406435 ns. These are estimated-parasitic pre-CTS results, not closed routed clocks. The serial fifth-stage optimization is absent. This study asks whether even a *hypothetical* feasible candidate clock improvement would survive execution dependencies.

## Explicit workload and boundary law

Consider synchronized batches of W mutually independent operations. The issue engine admits at most I operations per cycle, and each batch is followed by either a barrier on all its results or an independent next batch. Let N be the number of batches, B the number of dependent transitions (0 <= B <= N-1), and L the issue-to-result-availability latency in cycles. Batch boundaries are respected even if the final issue cycle has unused slots. The exact final completion time is

    C(N,W,I,L,B) = N * ceil(W/I) + B*(L-1) + L-1.

This is a deliberately narrow model: it is **not** a GPU trace, not a scheduler implementation, and not a full latency/occupancy/port-pressure model. I must be determined separately from measured bank compatibility, mask overlap, RF port limits, occupancy and control overhead. It cannot be assumed to equal the physical issue width.

For baseline latency Ls and candidate latency Lc, hypothetical feasible clock-frequency ratio r = fc/fs, and equal issue capacity I, the compute-only throughput gain is

    G = r * C(N,W,I,Ls,B) / C(N,W,I,Lc,B) - 1.

The candidate wins **only if** r > Cc/Cs. For large N with barrier fraction q=B/(N-1), Ls=1 and Lc=2, the limiting threshold is r > 1 + q/ceil(W/I). The exact finite-N threshold is used in the executable. Under an ideal shared external bandwidth ceiling M (ops per *serial-clock-time* unit), the upper-envelope gain is min(r*NW/Cc,M)/min(NW/Cs,M)-1. This ideal cap can hide compute benefits; it is **not** a burst-accurate memory simulator.

**Interpretation:** With no feasible clock improvement (r=1), the extra pipeline latency cannot improve throughput in this model and harms dependency-heavy regimes. An additional RF stage does not automatically preserve useful throughput merely because initiation interval remains one.

## Exploratory synthetic test results

Executable: `python3 research/v296/retiming_dependency_boundary.py --self-test --study`. A separate cycle-event implementation checks the closed form by issuing individual operations and scheduling completion events; 300 deterministic randomized cases passed locally in the equivalent development implementation. The committed implementation must also pass hosted CI before its results are treated as reproduced.

Each row uses 257 batches; clock ratios are **hypothetical** and not extracted from the failed physical timing runs. The seed 72811 cases are synthetic exploratory checks, **not prospectively registered real-workload holdouts**.

| Workload regime | W | I | Barrier fraction | Hypothetical r | Exact minimum r | Compute-only gain |
|---|---:|---:|---:|---:|---:|---:|
| Independent, predicted win | 32 | 4 | 0 | 1.05 | 1.000486 | +4.949% |
| One dependent wavefront, predicted no-win | 4 | 4 | 1 | 1.05 | 2.000000 | -47.500% |
| Alternating barriers, predicted no-win | 16 | 4 | 0.5 | 1.10 | 1.125486 | -2.264% |
| Independent but external bandwidth-saturated | 32 | 4 | 0 | 1.05 | 1.000486 | **0% capped** |
| Exploratory random barriers, seed 72811 | 11 | 3 | 0.359375 | 1.08 | 1.090467 | -0.960% |
| Exploratory random high occupancy, seed 72811 | 64 | 4 | 0.359375 | 1.05 | 1.022617 | +2.678% |

The last row is not evidence of a physical win: the 5% clock improvement is invented solely to test the boundary. Actual V296 and serial controls both remain timing-infeasible. No real dependent GPU workload or memory trace was run.

## Falsification implications and next experiment

1. The retiming's +1-cycle latency has a **quantifiable dependency penalty**, which may overwhelm any modest frequency benefit. It is incorrect to equate unchanged issue admissions with unchanged useful workload throughput.
2. The current tile-slice testbench checks independent RF values and one-cycle delayed outputs. It does **not** model dependent instruction hazards, bypassing, scoreboard stalls, cache misses, or memory-ordering semantics. Real traces and a dependency-aware simulator are required.
3. V296's arbitration and serial one-hot have identical admissions at fixed clock and resource counts. This experiment does not create a second architecture mechanism or rescue the unclosed design.
4. The strongest serial fifth-stage repair and equal-consumed-area physical implementation remain mandatory. The existing 3.5 ns +50 ps setup/hold/electrical/DRC gate is unchanged. If the physical and bandwidth gates erase the gain, reject V296's GPU-performance claim.
5. Before final evaluation, freeze real prospective dependency/compatibility/bank-conflict regimes and run unseen traces. A predictive law must incorporate measured compatibility probability, mask overlap, port pressure, occupancy, and control overhead, not substitute this narrow batch model for them.

**World-class gate remains unmet.** No routed timing closure, switching power, realistic integrated GPU throughput gain, or RTX-5090 equivalence is claimed. Kernellum PR #119 is unaffected.
