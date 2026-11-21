# V317 frozen stochastic workload-transfer gate (2026-11-02)

## Scope and evidence tier

This protocol tests the **previously frozen** legal-clock resource law from `LEGAL_CLOCK_CROSSOVER_PHYSICAL_FALSIFICATION_20261102.md` using an independently implemented seeded event simulation. Physical inputs are measured Nangate45 routed *control* areas (source/pairwise 7244.78/6576.58 um2 at 2.050 ns; 7096.08/6560.36 um2 at 2.200 ns). The 40,000-um2 other-tile cost, 1,170,000-um2 area budget, tile replication, occupancy, service arrivals, and shared bandwidth are **hypothetical**. No SRAM, datapath, GPU IPC, or calibrated power is represented.

The earlier legal-clock report was committed before these simulations and froze three named cases:
- W: backlogged, b=1.10, pair/source per-tile service ratio q=1.00, expected 25/24 = 1.0416667.
- N: backlogged, b=0.95, q=1.00, expected 1.0000000.
- R: backlogged, b=1.10, q=0.95, expected 25*0.95/24 = 0.9895833.

Here b is sustainable shared bandwidth relative to 24 source tile-opportunities/cycle. The independent simulator must implement **per-tile Bernoulli service opportunities**, a work-conserving shared output queue, and a fractional bandwidth-credit server, without importing or calling the analytic formula. Source tile opportunity probability is 1; pairwise is q. The pairwise per-tile probability is an abstract occupancy/control/bank-port availability factor, **not measured** from RTL. Both use identical clock and shared bandwidth. No simulated controller Fmax multiplier.

## Frozen held-out scenarios, before implementation/results

For both 2.050 and 2.200 ns physical area rows, require 24 source and 25 pairwise tiles at the frozen budget. Test four *additional* regimes not used in the three-case calibration:

| ID | b | q | Predicted ratio | Purpose |
|---|---:|---:|---:|---|
| H1 | 1.07 | 0.97 | 1.0104167 | modest unconstrained win |
| H2 | 1.02 | 0.90 | 0.9375000 | occupancy/control loss |
| H3 | 0.88 | 0.97 | 1.0000000 | shared-bandwidth saturation |
| H4 | 1.01 | 0.99 | 1.0100000 | bandwidth-clipped win |

Two equal-resource controls: E1 uses 24 vs 24 tiles, b=1.10, q=1.00 (1.0000000); E2 uses 24 vs 24, b=1.10, q=0.95 (0.9500000). These explicitly prevent a controller-only throughput claim.

Simulation: 5 independent seeds [17, 71, 173, 719, 1723], 120,000 measured cycles plus 4,096 warm-up cycles per variant; each tile can emit at most one useful operation per cycle, and completed operations wait in a **synthetic unbounded** shared queue. Work-conserving bandwidth-credit service is independent of tile generation. Compare mean ratio to frozen prediction with **absolute tolerance 0.002**; report all seeds and queue growth. Also evaluate an **unqueued** b=0.75, q=0.75 both sides control; explicitly do not apply the backlogged law to that case.

## Falsifiers and claims

Fail if any of the 3 original or 4 held-out backlogged means differs by >0.002, or equal-resource E1 differs by >0.002. If predictions fail, preserve all rows and do not refit the law. Report per-seed variance. A pass only validates a conditional **synthetic workload model** and cannot prove tile reinvestment, RF port feasibility, real workload speedup, or novel GPU architecture. No RTX-5090-equivalence claims.

Next hard physical gate remains SRAM/datapath and multi-corner integration, stronger legal-source control, and independent activity-calibrated power.
