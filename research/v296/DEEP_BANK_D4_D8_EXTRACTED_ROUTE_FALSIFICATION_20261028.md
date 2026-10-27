# V296 deep-bank routed physicality falsification — 2026-10-28

**Decision: reject any matched feasible D4/D8 claim at the frozen 3.5 ns clock.** Completed [Actions run #40557136436](https://github.com/sushxnthd/vektor/actions/runs/40557136436) produced two full physical measurements and two 165-minute timeouts. Both completed runs fail setup and capacitance. Both independent aggregate jobs correctly returned `INCOMPLETE_NO_TILE_PHYSICAL_CLAIM` (exit 3). A physical job reporting GitHub Actions success means its evidence uploaded, **not** that its circuit passed timing. Original source commit: `6c5e61f30a483ce1112e143e3d8a6048014e3939`.

## Frozen extracted-RC results

| Depth | Controller | Execution | Final area (µm²) | Setup (ns) | Hold (ns) | Cap | Slew | Feasibility |
|---|---|---|---:|---:|---:|---:|---:|---|
| D4 | V296 pairwise | timeout (124) | — | — | — | — | — | not established |
| D4 | optimized serial | complete (0) | 23,265.690 | -1.316510 | +0.002572 | 6 | 0 | FAIL |
| D8 | V296 pairwise | complete (0) | 28,984.157 | -0.684592 | +0.010986 | 1 | 0 | FAIL |
| D8 | optimized serial | timeout (124) | — | — | — | — | — | not established |

Evidence tier: OpenROAD post-CTS propagated-clock detailed-route OpenRCX at 2× RC, **not foundry signoff**. The frozen Tcl uses `repair_timing -setup -slack_margin 0.250` and `repair_timing -hold -slack_margin 0.025`. Audit limits: 250 ps final setup guard, nonnegative final hold, zero cap/slew violations, integrated area <=30,000 µm². All measured data were transcribed from the aggregate logs. All four original artifact ZIPs were subsequently downloaded, independently SHA-256-rehashed and matched the GitHub upload-log digests. The original OpenROAD results were not rerun.

## Conditional physical boundary

For unchanged critical-path delays, the setup-guard clock-period requirement is:

`P_min,conditional = 3.500 ns + max(0, 0.250 ns - measured_setup_slack)`.

- **D8 V296:** +0.934592 ns setup recovery at 3.5 ns, or conditional period >= **4.434592 ns** (<=225.50 MHz). Remaining area headroom: **1,015.843 µm²**. Cap violations: **1**.
- **D4 optimized serial:** +1.566510 ns recovery, or conditional period >= **5.066510 ns** (<=197.37 MHz). Cap violations: **6**.

These are **conditional fixed-delay bounds**, not measured Fmax. They are **not an architecture frequency comparison**, because they are from different depths. Slowing the clock cannot by itself repair the observed capacitance violations. At 4.434592 ns, D8 V296 has 78.92% of the nominal 3.5 ns clock rate; no measured per-cycle advantage is available to offset that loss. The previous model predicts zero same-clock admission advantage in its matched setting, but that model is not a GPU benchmark.

## Scientific rejection and next decisive experiment

The hypothesis that a D4/D8 **mapped-area advantage** alone transfers to a feasible integrated tile at 3.5 ns and 2× RC is **falsified for this implementation**. Neither functional equivalence nor the architecture mechanism is thereby disproved. **Never compare D8 V296 against D4 serial as a matched physical result.**

**Frozen next kill test:** inspect the exact timeout stages and worst setup endpoints from the partial artifacts. Any shared physical repair must keep architecture RTL, resources, 3.5 ns clock, 2× RC, area cap and all gates fixed for both contestants. Require completed, feasible D4 and D8 pairs before comparing area, throughput or traffic. If no symmetric repair restores timing/electrical feasibility within budget, retire V296 as a deep-bank physical implementation. V287 remains retired; do not claim RTX-5090 equivalence.

Reproduce the independent fail-closed checker:

```bash
python3 research/v296/deep_bank_route_gate_falsification.py \
  research/v296/DEEP_BANK_D4_D8_EXTRACTED_ROUTE_FALSIFICATION_20261028.json --self-test
```

It tests missing physical metrics, false success status, independent setup/cap failures, NaN and area overflow. It does **not** replay the original OpenROAD run or open workload holdouts.

## Original-artifact route-convergence forensics (same run)

All four original artifact ZIP SHA-256 checks passed independently. The two timeouts are **real detailed-route convergence/runtime failures**, not merely missing uploads or dependency-install failures:

| Depth / controller | Detailed-route iterations completed | Final completed-iteration DRC count | Last partial state |
|---|---:|---:|---|
| D4 pairwise | 6 | **19,252** | Iteration 6, 40% progress, **19,107** transient violations |
| D4 optimized serial | 26 | **0** | Routed and extracted; fails setup and 6 capacitance limits |
| D8 pairwise | 12 | **0** | Routed and extracted; fails setup and 1 capacitance limit |
| D8 optimized serial | 0 | unavailable | Iteration 0, 80% progress, **33,054** transient violations |

The partial counts are **not final signoff DRC totals**. D4 pairwise was still reducing violations slowly, from 30,587 after iteration 0 to 19,252 after iteration 5. D8 serial had not completed its first detailed-route iteration before the timeout. No extrapolation of eventual completion is defensible.

In the completed D8 pairwise design, the lone capacitance violation at `_15191_/ZN` is **0.830492 fF over its 106.810997 fF limit**. The small capacitance excess does not resolve the much larger **934.592 ps** setup-guard deficit. The D4 serial control also has six capacitance violations. Both completed designs had zero reported final detailed-route DRC violations; this does **not** imply timing/electrical feasibility.

**Updated kill-test priority:** physical convergence is a first-class experimental variable. Before another expensive matched run, examine routing-density/track congestion and setup critical paths in the original partial artifacts. Do not increase timeout alone and mistake extra compute for a mechanism improvement. If applying congestion relief, use symmetric floorplan/resource constraints and repeat both controllers at both depths. Do not compare a timed-out partial design to a completed design.

Independent original-artifact replay:

```bash
python3 research/v296/deep_bank_detailed_route_forensics.py /path/to/downloaded-artifact-zips
```

The four original ZIPs are [D4 pairwise](https://github.com/sushxnthd/vektor/actions/runs/40557136436/artifacts/12770962531), [D4 serial](https://github.com/sushxnthd/vektor/actions/runs/40557136436/artifacts/12769708334), [D8 pairwise](https://github.com/sushxnthd/vektor/actions/runs/40557136436/artifacts/12769775926), and [D8 serial](https://github.com/sushxnthd/vektor/actions/runs/40557136436/artifacts/12769658115).
