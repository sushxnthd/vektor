# V296 deep-bank routed physicality falsification — 2026-10-28

**Decision: reject any matched feasible D4/D8 claim at the frozen 3.5 ns clock.** Completed [Actions run #40557136436](https://github.com/sushxnthd/vektor/actions/runs/40557136436) produced two full physical measurements and two 165-minute timeouts. Both completed runs fail setup and capacitance. Both independent aggregate jobs correctly returned `INCOMPLETE_NO_TILE_PHYSICAL_CLAIM` (exit 3). A physical job reporting GitHub Actions success means its evidence uploaded, **not** that its circuit passed timing. Original source commit: `6c5e61f30a483ce1112e143e3d8a6048014e3939`.

## Frozen extracted-RC results

| Depth | Controller | Execution | Final area (µm²) | Setup (ns) | Hold (ns) | Cap | Slew | Feasibility |
|---|---|---|---:|---:|---:|---:|---:|---|
| D4 | V296 pairwise | timeout (124) | — | — | — | — | — | not established |
| D4 | optimized serial | complete (0) | 23,265.690 | -1.316510 | +0.002572 | 6 | 0 | FAIL |
| D8 | V296 pairwise | complete (0) | 28,984.157 | -0.684592 | +0.010986 | 1 | 0 | FAIL |
| D8 | optimized serial | timeout (124) | — | — | — | — | — | not established |

Evidence tier: OpenROAD post-CTS propagated-clock detailed-route OpenRCX at 2× RC, **not foundry signoff**. The frozen Tcl uses `repair_timing -setup -slack_margin 0.250` and `repair_timing -hold -slack_margin 0.025`. Audit limits: 250 ps final setup guard, nonnegative final hold, zero cap/slew violations, integrated area <=30,000 µm². All measured data were transcribed from the aggregate logs. Artifact ZIP SHA-256 values in the JSON are **reported by GitHub upload logs, not independently rehashed in this run**.

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
