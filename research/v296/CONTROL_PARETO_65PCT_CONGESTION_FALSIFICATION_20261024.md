# V296 high-RC control challenge: 65%-density congestion falsification (2026-10-24)

**Decision: FOUR-WAY PHYSICAL GATE FAILED / INCOMPLETE.** This is a negative physical result, not a V296 win. Sole active architecture remains V296 pairwise bank-conflict admission; V287 remains retired. The earlier failed six-case gate is not superseded. Prospective workload holdouts remain sealed.

## Frozen experiment and observed failure

The uniform 0.65 global-placement-density amendment was frozen before [GitHub Actions run 40054812822](https://github.com/sushxnthd/vektor/actions/runs/40054812822), artifact [12545416823](https://github.com/sushxnthd/vektor/actions/runs/40054812822/artifacts/12545416823), ZIP SHA-256 `08d054e0d3048ccbef0614cf861e6502f8d8f5597fc5ca7afaff528e830707c6`. The toolchain and independent checker self-test passed. The experiment then stopped in the **first original-controller contestant**, before serial one-hot, parallel one-hot, or V296 ran.

The original control's fourth repair completed global routing but retained **two maximum-capacitance violations** and negative setup slack. Its additional control-only fifth repair expanded the cell footprint and **failed global routing with OpenROAD `GRT-0116` (congestion)**. The run failed and preserved its partial evidence. Neither fourth nor fifth stage provides extracted-RC timing or detailed-route DRC; the following are intermediate **placed/global-route** measurements only.

| Original-controller stage | Cell area (µm²) | Setup slack (ns) | Max-slew / max-cap | Cell/core utilization |
|---|---:|---:|---:|---:|
| Fourth repair, placed | 9796.248257 | -1.246551 | 0 / 5 | 69.482% |
| Fourth repair, global-routed | 9796.248257 | -0.953935 | 0 / 2 | 69.482% |
| Fifth control-only repair, placed | 10208.814238 | -1.435621 | 0 / 4 | 72.408% |
| Fifth control-only global route | **FAIL** | Not measured | Unknown | Not routed |

These figures are transcribed from the hosted job log, not independently reconstructed from DEF. The earlier 0.45-density physical result is a separate run and must not be compared as a matched measurement.

## Reproducible capacity and repair sensitivity boundary

Let `A` be current standard-cell area, `C` the unchanged snapped core area (14,099.064 µm²), `L` the preregistered common area ceiling (7,400 µm²), and `r` an *additional* relative cell-area change. Then the area qualification condition is

`A(1+r) <= L`, equivalently `r <= L/A - 1`.

This is a **necessary cell-area constraint**, not a routing or timing sufficiency law. The observed fourth-stage original requires at least **24.461% area reduction** to fit the frozen ceiling; after the fifth repair it requires **27.514% reduction**. The fifth repair added **412.566 µm² (4.211%)**, rather than reducing area, and its 10,208.814 µm² footprint exceeds the ceiling by **2,808.814 µm² (37.957%)**.

The configured 65% **global-placement target is not a hard cap on later repaired utilization**. Indeed, measured repaired utilization grew to 69.482% and then 72.408%. Congestion is directly reported by OpenROAD, but its onset cannot be inferred from utilization alone without congestion maps and routing topology. The previous forecast that raising initial placement density would be sufficient for a four-way detailed-route comparison is **falsified**.

## Prospective continuation, without changing physical constraints

The next attempt will retain the exact 65% placement setting, core/die, 3.5 ns clock, 2× RC, Nangate45 cells, 7,400 µm² ceiling, four repair rounds for every variant and a fifth control-only round. It changes **only execution ordering and failure collection**, not the physics: evaluate V296 first, then serial one-hot, parallel one-hot, and original. Preserve all failures and continue to the next contestant even when one routes unsuccessfully. The independent four-way checker must still **fail closed** on any missing DEF, SPEF, or full extracted result; a partial V296 result must never be advertised as a matched four-way win.

**Pre-outcome hypotheses:** (H1) V296 may still complete a detailed route under 65% density, but no area/timing benefit is assumed. (H2) the original control's fifth-round route is expected to fail again if the flow is deterministic, providing a reproducibility check. (H3) no four-way pass is possible unless all contestants complete the frozen gate; the area ceiling is binding on the measured original fourth/fifth stages. All new outcomes must be compared only within the new attempt and previous negative results preserved.

A future legitimate alternative is to **preregister a new resource-matched floorplan and optimization budget** before rerunning all architectures, rather than retrospectively enlarging only the control or relaxing area/timing criteria. No unseen workload, CTS, power, GPU throughput, or RTX-5090-equivalence claim is supported.

Kernellum PR #119 and its holdouts are untouched.
