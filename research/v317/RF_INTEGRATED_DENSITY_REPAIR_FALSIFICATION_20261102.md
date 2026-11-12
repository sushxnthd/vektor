# V317 integrated issue-control: legal-source density-repair falsification (2026-11-02)

## Immutable evidence and audit status

Frozen *before* routing: [density-repair protocol](FROZEN_INTEGRATED_DENSITY_REPAIR_CHALLENGE_20261102.md). Matched four-route [OpenROAD run #41372770907](https://github.com/sushxnthd/vektor/actions/runs/41372770907) completed with all four make exit codes zero; [raw 467-file artifact #13109979385](https://github.com/sushxnthd/vektor/actions/runs/41372770907/artifacts/13109979385), digest `sha256:b650ecd2d2edc2ab0ea74e1142993b135c50592d204b86a201c4a072a`. Source commit `f5247166cab17ae91074a17f55c6a32031dc9fbb`, ORFS image `sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8`. Independently parsed raw ZIP with Python zipfile and original `6_report.json`, `5_2_route.log`, `3_3_place_gp.log` and `6_report.log` (not prior summary tables). [Reproducible independent checker](rtl/audit_integrated_density_repair.py) and [hosted audit workflow](../../.github/workflows/v317-integrated-density-raw-audit.yml) are committed; **hosted checker outcome remains unconfirmed** at the time of this report.

Nangate45 typical; 356 sequential cells, no macros; 2.000 ns target, 10-fF loads, 120 x 120 um die / 112 x 112 um core, seed 7, ABC area mapping, timing-driven placement, extracted RC. Same 32-wave issue controller and 4096-cycle functional-equivalence PASS (13,153 accepted operations). This is **post-hoc density tuning**, not a fresh held-out seed.

## Complete matched measurements

| Density addon | Variant | Actual initial target density | Routed area (um2) | Fmax (MHz) | Setup slack (ps) | Setup violations | Hold slack (ps) | Power proxy (mW) | Wire (um) | 2-ns legal? |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 0.05 | source | 0.62050 | 7539.24 | 499.629 | -1.483 | 1 | +16.431 | 5.63016 | 58660 | **NO** |
| 0.05 | pairwise | 0.59200 | 6609.04 | 526.785 | +101.692 | 0 | +14.710 | 5.21544 | 55631 | **YES** |
| 0.35 | source | 0.74350 | 7407.83 | 498.355 | -6.600 | 10 | +21.220 | 5.49939 | 55629 | **NO** |
| 0.35 | pairwise | 0.72400 | 6577.91 | 518.782 | +72.408 | 0 | +14.582 | 5.17096 | 51886 | **YES** |

All four have zero final route DRC, zero reported hold, max-cap, max-slew and max-fanout violations. Original source is nevertheless **timing-illegal** at 2 ns in both conditions. Extracted-RC reports were present; route lengths are from original route logs. The power figures are OpenROAD default-activity proxies, not measured switching power or energy per instruction.

The physical intervention is genuine: global-placement logs explicitly report `PLACE_DENSITY_LB_ADDON` 0.05 and 0.35 and corresponding changed target densities, rather than only changing a config label. At matched add-on 0.05, pairwise saves **12.34% area**, improves controller Fmax **5.44%**, reduces default-activity power proxy **7.37%** and wire length **5.16%**. At 0.35, respective figures are **11.20%, 4.10%, 5.97%, 6.73%**.

## Frozen adversarial hypotheses and conclusion

1. **Source repair possibility:** falsified for both tested density settings at seed 7; the closest source miss is only **1.483 ps**. This does not establish source cannot be legally repaired by a different knob or physical corner.
2. **Pairwise retains area advantage:** survives both matched density settings, including the better source area at 0.35. The source's smallest observed area is **7407.83 um2**, but that implementation is not legal at 2 ns.
3. **Electrical closure:** all four routes meet reported DRC/hold/cap/slew/fanout checks; only pairwise closes setup.
4. **Same-clock grant/port throughput:** exactly **1.000x intrinsic** by functional equivalence. The 4.10-5.44% controller Fmax advantage is *not* a GPU clock or IPC result.

Combined with the earlier [three-seed audit](RF_INTEGRATED_SEED_CHALLENGE_FALSIFICATION_20261102.md), there are **three distinct physical seeds** and **two additional density variants at a reused seed**, not five independent seeds. Pairwise survives the tested typical-corner conditions. Do not infer statistical yield or multi-corner robustness.

## Predictive boundary and kill condition

Let `A_other` be the unmeasured rest-of-tile area, `A_x` the measured issue-control area, `T_other` the independently measured other-tile critical period, `T_x` the controller period, `B` total area budget, `r` service per tile per cycle, `L` offered demand, and `C` shared bandwidth ceiling:

```
N_x = floor(B / (A_other + A_x))
Q_x = min(L, C, N_x*r / max(T_other, T_x))
G = Q_pairwise / Q_source
```

If `T_other >= max(T_source,T_pairwise)`, both systems buy the same tile count, and `C` or `L` saturates both, then **G=1**. Pairwise can improve *system* throughput only if it permits an additional usable tile or shortens the actual tile critical period without encountering shared ceilings. Neither condition has been measured with SRAM and datapath. The mechanism is **bank-credit logic implementation**, not V287 warp fusion; mask compatibility/overlap probabilities are not operative variables for these grant-equivalent RTL variants.

**Next kill gate:** compare best legally timing-repaired source with pairwise under matched constraints, then vary extracted load and process corner and integrate RF SRAM, datapath and traffic. If legal source closes the area/power gap or the full tile is limited by another path/bandwidth, downgrade V317 to a local physical optimization, not a GPU performance breakthrough. No RTX 5090 equivalence claim.
