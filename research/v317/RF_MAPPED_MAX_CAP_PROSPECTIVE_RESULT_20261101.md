# V317 independent mapped-netlist max-capacitance audit: prospective results (2026-11-01)

## Evidence tier and preregistration
The frozen protocol [FROZEN_RF_MAX_CAPACITANCE_20261101.md](FROZEN_RF_MAX_CAPACITANCE_20261101.md) was committed at `1abfd0f` before the independent parser, tests, synthesis or final measurement. Source-pinned [GitHub Actions #41328336392](https://github.com/sushxnthd/vektor/actions/runs/41328336392) **PASSED** at `9fe1851`. The pinned Nangate45 typical Liberty has blob SHA `90e4afb274cfc6514c587c434c77903d554117d1` and `capacitive_load_unit (1,ff)`. The workflow reruns the identical source-fixed and pairwise-fixed Yosys/ABC mapping recipe from the earlier matched buffer experiment, checks independent adversarial parser fixtures, and uploads raw mapped Verilog, synthesis logs and the machine-readable full audit. Several initial parser incompatibilities with real Yosys escaped identifiers and a direct-primary-input grant were exposed by CI, preserved and repaired before the successful run; no negative physical result was silently discarded.

## Three prospective output-pin predictions
| Output stage | External load | Nangate45 max_capacitance | Margin | Frozen prediction | Result |
|---|---:|---:|---:|---|---|
| BUF_X1 | 24 fF | 60.6537 fF | +36.6537 fF | pass | PASS |
| BUF_X2 | 100 fF | 121.155 fF | +21.155 fF | pass | PASS |
| BUF_X1 | 100 fF | 60.6537 fF | -39.3463 fF | fail | FAIL as predicted |

All three frozen predictions survived, for both fixed-priority implementations. The negative BUF_X1/100-fF case is **not electrically admissible**, even if a raw timing path is printed.

## Complete mapped cell-pin capacitance accounting
At both nominal matched repair points (BUF_X1/24 fF and BUF_X2/100 fF), the independent auditor found:

| Matched fixed-priority core | Mapped instances | Characterized mapped output drivers | Internal max-cap violations | Smallest internal cap margin |
|---|---:|---:|---:|---:|
| Original bank-mask | 731 | 731 | **0** | **+0.680998 fF** |
| Pairwise bank-credit | 200 | 200 | **0** | **+3.838028 fF** |

The narrowest original-core margin is at a NOR4_X1/ZN output, load 9.790302 fF against max 10.4713 fF. The narrowest pairwise-core margin is at NOR4_X1/ZN, load 6.633272 fF against the same limit. These are **zero-wire, mapped input-pin-capacitance sums**. They are not routed parasitic capacitances. The original design's 0.681-fF minimum margin is particularly vulnerable to additional wire capacitance, but this does not prove that routing violates the limit.

### Direct-input grant caveat
Both netlists contain `assign grant[0] = request_valid[0];`. This grant is driven directly by a primary input, not a characterized mapped output cell. The auditor correctly identifies and reports one uncharacterized primary-input driver per core. It adds the selected buffer input capacitance (BUF_X1/A: 0.974659 fF; BUF_X2/A: 1.779209 fF), but **cannot certify the upstream driver**. Consequently, the new result is characterized **mapped-cell max-capacitance admissibility**, not complete electrical signoff.

## Research consequence and hard limits
The previous matched BUF_X1/24-fF and BUF_X2/100-fF max-transition repairs now also pass **mapped-cell max-capacitance** in the pinned ideal-wire library model, but the original core has a very narrow internal cap margin. There is no claim of placed/routed timing closure, extracted wire RC, primary-input driver legality, setup/hold signoff, power improvement, clock increase or GPU throughput. Grant decisions and bank ports remain unchanged; intrinsic service at equal clock and tile count is 1.000x.

**Next decisive physical gate:** place and route the same mapped fixed-priority cores under matched constraints, extract wire capacitance and resistance, check max-transition/max-capacitance and timing after parasitics, and test actual tile criticality. If the 0.681-fF original margin disappears under RC, report the failure; if the pairwise design also violates or cannot meet the integrated tile period, reject the throughput claim. Do not replace V317 with historical V287 or create another mechanism/branch/PR. Preserve Kernellum PR #119.

Reproduce: `python3 -m unittest research.v317.rtl.test_audit_rf_max_cap -v`; hosted `.github/workflows/v317-rf-max-cap.yml`. The workflow's uploaded artifact contains `audit.json`, both mapped netlists, synthesis logs, pinned Liberty and source SHA.
