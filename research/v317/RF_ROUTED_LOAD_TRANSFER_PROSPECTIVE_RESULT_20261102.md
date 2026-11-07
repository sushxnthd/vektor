# V317 prospective 10/40-fF routed-load transfer: physical result (2026-11-02)

## Provenance and frozen predictions
The [immutable protocol](FROZEN_RF_ROUTED_LOAD_AND_AREA_PHASE_20261102.md) was committed before the 40-fF results. Raw evidence is [GitHub Actions #41343090875](https://github.com/sushxnthd/vektor/actions/runs/41343090875), [artifact 13097659391](https://github.com/sushxnthd/vektor/actions/runs/41343090875/artifacts/13097659391), source SHA `01edebed092c65c264d42814a927614338b8ef9e`, official ORFS container digest `sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8`. The source SHA is one ancestor behind the report-only branch head; the compared RTL and workflow were unchanged. The same 40-flop registered wrapper, 60x60-um die, 52x52-um core, Nangate45 typical, 2.0-ns clock, and matched input drive/delay were used. Only the grant-output load was changed between 10 and 40 fF.

The complete four-case physical workflow **passed** and uploaded 469 files. The [independent raw-artifact checker](rtl/audit_routed_load_transfer.py) reads the ZIP directly, verifies source SHA, container digest, constraints, all four exit codes, timing/electrical violation counts, final detailed-route DRC and antenna counts, area, wire length, power proxy, and frozen 10-fF replication tolerance. A [separate hosted audit](../../.github/workflows/v317-rf-routed-load-audit.yml) was added for reproducibility; do not claim it passed until its run is inspected.

## Routed and extracted-RC measurements
The OpenROAD final reports contain RC extraction evidence (RCX-0045). Periods below are 1/fmax from the final 6_report.json; area is standard-cell area excluding fill cells. The power column is the tool's **default-activity estimate**, not measured silicon power or workload-calibrated switching.

| Variant | Grant load | Cell area (um2) | Minimum period (ns) | Setup slack (ns) | Hold slack (ns) | Routed wire (um) | Default-activity power (mW) | Final DRC | Max slew/cap/fanout violations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Original fixed | 10 fF | 1316.170 | 1.556168 | +0.443832 | +0.003142 | 9789 | 0.377968 | 0 | 0/0/0 |
| Pairwise fixed | 10 fF | 583.338 | 0.575546 | +1.424450 | +0.008490 | 3550 | 0.277924 | 0 | 0/0/0 |
| Original fixed | 40 fF | 1316.170 | 1.556168 | +0.443832 | +0.003142 | 9789 | 0.383185 | 0 | 0/0/0 |
| Pairwise fixed | 40 fF | 583.338 | 0.584515 | +1.415480 | +0.008490 | 3550 | 0.282149 | 0 | 0/0/0 |

All four final reports show zero setup and hold violation counts, zero detailed-route DRC, zero reported max-slew, max-cap and max-fanout violations, and zero antenna-violating nets. The original period remains unchanged at 40 fF because its reported limiting clock path does not respond to the output-load increase; **do not interpret this as general load insensitivity**.

## Prospective decision
- **P1 PASS:** both 10-fF cases are electrically admissible under the reported constraints; original/pairwise areas and periods replicate the prior physical result within the frozen 10% tolerance.
- **P2 PASS as NO-ARCHITECTURE-WIN control:** at equal clock, identical grants and RF ports imply exactly **1.000x intrinsic service throughput**, regardless of the physical optimization. This is a semantic identity, not a measured workload experiment.
- **P3 PASS:** both 40-fF routes are admissible under the reported checks. Pairwise retains a **55.679%** routed cell-area reduction, **63.735%** routed wire-length reduction, and **2.6623x** original/pairwise isolated minimum-period ratio. At 10 fF the corresponding period ratio is **2.7038x**.
- The default-activity total power proxy is **26.4689%** lower at 10 fF and **26.3674%** lower at 40 fF for pairwise. These numbers are neither a power-signoff result nor a prediction of GPU board power. The pairwise period increases by approximately 1.56% when output load rises from 10 to 40 fF, while its cell area and routed wire length remain unchanged.

## Mechanism and kill boundary
The surviving single mechanism remains **fixed-priority pairwise bank-credit**, a grant-equivalent implementation of the original fixed-priority bank-mask arbiter. The strongest matched same-policy control here is the original fixed-priority implementation with identical RF-bank ports, 40-flop wrapper, die/core footprint, timing constraints and loads. The positive result is a physical **implementation** optimization, not a novel scheduling or GPU architecture throughput mechanism.

For an integrated tile, the conditional resource law remains
`N_x=floor(B/(A_other+A_arbiter,x))`, `T_x=max(T_other,T_arbiter,x)`, and
`R_x=min(offered,shared_bandwidth,N_x*work_per_tile_cycle/T_x)`.
If both variants fit the same number of tiles, the arbiter is noncritical and shared bandwidth/ports are unchanged, **G=1**. If shared bandwidth saturates both, **G=1** even if area permits another tile. The previously frozen 18,325/41,316 hypothetical extra-tile budget phases do not represent a real GPU workload distribution.

**NO-GO for unconditional GPU IPC and RTX-5090 equivalence.** Retain pairwise only as an isolated routed, single-corner implementation optimization. Next decisive work: integrate the actual register-file/SRAM area, port counts, bank-access traffic, occupancy and tile clock paths; compare with a physically costed optimized equal-resource baseline; run multi-corner/OCV/coupling sensitivity and workload-calibrated power. Kill the architecture-performance claim if these constraints erase the gain. Kernellum PR #119 remains separate and untouched.
