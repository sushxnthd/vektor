# V296 original-routed coupling and switching-correlation boundary: prospective result (2026-10-25)

**Evidence tier:** completed SHA-locked postprocessing of the **original** matched post-route OpenRCX SPEFs, with independent declared-net-total and algebraic checks in [hosted run 40188542339](https://github.com/sushxnthd/vektor/actions/runs/40188542339) (**success**). This is a **conditional external-capacitance switching-energy proxy**, not measured GPU power, not physical closure and not a frequency/throughput improvement.

The protocol and corner selection were frozen in [ORIGINAL_SPEF_COUPLING_ACTIVITY_PREREG_20261025.md](ORIGINAL_SPEF_COUPLING_ACTIVITY_PREREG_20261025.md) **before** reading the `*CAP` records. Executable parser: [coupling_activity_boundary.py](coupling_activity_boundary.py). Raw [hosted numerical audit artifact 12597611559](https://github.com/sushxnthd/vektor/actions/runs/40188542339/artifacts/12597611559).

## Extracted physical decomposition

| SHA-locked original SPEF metric | V296 pairwise | Serial one-hot | V296 relative change |
|---|---:|---:|---:|
| Declared D_NET cap sum (pF) | 51.546319 | 59.086010 | -12.7605% |
| One-terminal ground cap Cg (pF) | **21.788331** | **24.937753** | **-12.6291%** |
| Unique two-terminal coupling Cc (pF) | **14.878993** | **17.074129** | **-12.8565%** |
| Unique coupling endpoint pairs | 155,792 | 177,552 | -12.25% |
| Coupling records including duplicates | 311,584 | 355,104 | -12.25% |
| Largest within-net-block coupling sum (pF) | **0.072017** | **0.063615** | **+13.21%** |
| D_NET sum minus (Cg + 2Cc), pF | +0.000001485 | -0.000000232 | near-zero |

The duplicate coupling records reconcile exactly to two records per unique endpoint pair. The independently parsed D_NET sums agree with the original physical audit to better than 1e-5 pF. The near-zero `D_NET - (Cg+2Cc)` residual confirms that the original extracted declared totals double-count each coupling capacitor in the per-net accounting. Therefore treating the sum of declared D_NET caps as physical energy **without** separating coupling is not justified.

## Frozen predictive boundary

Assume homogeneous squared voltage transition `E[dV_i^2]=alpha V^2` and normalized signed cross-net transition covariance `rho = E[dV_i dV_j]/(alpha V^2)`. The external capacitive switching-energy proxy is

`E_ext = (alpha V^2/2) [Cg + 2 Cc (1-rho)]`.

The exact activity-ratio break-even is

`alpha_V296/alpha_serial = [Cg_serial + 2 Cc_serial(1-rho_serial)] / [Cg_V296 + 2 Cc_V296(1-rho_V296)]`.

For the **preregistered equal-correlation corners** and equal activity:

| Common rho | V296 effective cap (pF) | Serial effective cap (pF) | V296 saving | V296/serial activity break-even |
|---:|---:|---:|---:|---:|
| -1 (opposite signed transitions) | 81.304304 | 93.234268 | **12.7957%** | 1.146732 |
| 0 (uncorrelated signed transitions) | 51.546318 | 59.086011 | **12.7605%** | 1.146270 |
| +1 (same signed transitions) | 21.788331 | 24.937753 | **12.6291%** | 1.144546 |

**Positive conditional finding:** V296 has lower extracted external-capacitive proxy than the serial control at all three *equal-correlation, equal-activity* corners. This follows from **both** lower Cg and lower Cc, not merely a smaller D_NET total. The boundary predicts that the advantage vanishes when V296 switches about **14.45%-14.67% more frequently** under the corresponding common-rho corner.

**Decisive negative finding:** this is **not robust to independent correlation regimes**. With V296 at rho=-1 and serial at rho=+1, V296's effective coefficient is **81.304304 pF versus 24.937753 pF** (3.26029x *worse*). Thus the independent-correlation guarantee is **falsified**, as frozen. A future trace study must measure signed switching covariance and activity *before* claiming lower dynamic power.

## Physical and architectural limits

The largest local coupling sum is worse for V296 despite aggregate Cg/Cc improvements. Net-level local RC, driver sizing, clock-tree power, internal-cell power, glitching, short-circuit power, voltage, occupancy and realistic workloads remain unmeasured. Uniform rho is a sensitivity model, not a measured net-activity distribution. The independent cross-check verifies numerical accounting and model algebra, not a full independent physical extraction.

Both original integrated implementations **still fail** the frozen 3.5 ns setup, hold and capacitance constraints (V296 setup -1.047895 ns, hold -0.036622 ns, cap violations 3; serial setup -1.859922 ns, hold -0.019796 ns, cap violations 3). Same-clock arbitration admissions are equal. **No integrated GPU speedup, physically feasible power reduction, or RTX-5090 equivalence is claimed.**

## Decision and next discriminator

Retain V296 as the **sole provisional mechanism**, V287 retired. Preserve this conditional positive law and the independent-correlation falsification together. The decisive next steps remain the separately running extracted critical-path identification, matched electrical/timing repair against an independently optimized equal-budget serial control, and prospective workload-derived per-net activity/covariance. Workload holdouts remain sealed. Kernellum PR #119 unchanged.
