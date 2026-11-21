# V317: prospective RF-proxy area-dilution boundary (2026-11-02)

This note was committed **while** the 16-bank RF-proxy physical experiment was still routing. No new physical results are used. The only inputs are two previously routed **controller-only** legal-clock comparisons. It is a sensitivity/null model, not a fitted GPU performance claim.

## Predictive law

If two grant-equivalent controllers have areas `A_s` and `A_p`, and the **same** additional banked-RF/datapath hardware contributes `R` standard-cell-equivalent area to each without placement or synthesis interactions, then the pairwise total-area saving is

```
S(R) = (A_s - A_p) / (A_s + R).
S(R) >= tau  <=>  R <= (A_s - A_p)/tau - A_s.
```

This is an explicit **dilution boundary**, not a positive IPC law. It predicts that any isolated controller saving approaches zero as real RF/datapath area dominates. It also supplies a direct falsifier: if the integrated routed area difference is not close to the isolated difference, additive common-area accounting fails, because physical optimization interacts with the added hardware.

## Prior legal-clock inputs and frozen 2% materiality threshold

| Previous controller route | Source (um2) | Pairwise (um2) | Controller saving (um2) | Maximum common R (um2) for >=2% integrated saving |
|---|---:|---:|---:|---:|
| 2.050 ns | 7244.78 | 6576.58 | 668.20 | 26165.22 |
| 2.200 ns | 7096.08 | 6560.36 | 535.72 | 19689.92 |

Illustrative sensitivity, **not** predicted 3.000-ns routed measurements:

| Hypothetical common R (um2) | 2.050-ns prior S(R) | 2.200-ns prior S(R) |
|---|---:|---:|
| 5,000 | 5.4570% | 4.4289% |
| 10,000 | 3.8748% | 3.1336% |
| 20,000 | 2.4526% | 1.9771% |
| 30,000 | 1.7941% | 1.4441% |

## Frozen interpretation of the ongoing integration

The prospective 3.000-ns [RF-proxy physical protocol](FROZEN_BANKED_RF_PROXY_TILE_GATE_20261102.md) independently requires >=2% area saving **only if both matched implementations are timing/electrically legal**. It must use the **new** 3.000-ns actual routed areas, not these 2.050/2.200-ns areas. Since the clock, placement, and synthesis change, the 535.72-668.20-um2 differences are **not** transferable calibrated predictions; they are an intentionally vulnerable null. A <2% integrated saving kills material area-win language. A timing failure blocks the legal comparison. Both implementations have the same grants/operands and therefore **1.000x intrinsic same-clock issue throughput**.

Even a surviving proxy-area saving cannot establish an extra GPU tile, SRAM macro legality, realistic power, GPU IPC, or RTX-5090-equivalent performance. The independent checker must inspect raw extracted-RC and DRC/electrical evidence rather than a success flag.
