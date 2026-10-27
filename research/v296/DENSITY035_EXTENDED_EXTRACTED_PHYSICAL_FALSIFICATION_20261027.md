# V296 density-0.35 matched extracted-RC falsification (2026-10-27)

## Frozen experiment and independent replay

The extended matched trial [Actions #40427986118](https://github.com/sushxnthd/vektor/actions/runs/40427986118) **completed** on 2026-10-27. Its GitHub Actions jobs all report `success` because the experiment deliberately preserves scientific failures rather than failing the hosting workflow. That status is **not** physical feasibility. The preregistered diagnostic [protocol](DENSITY035_EXTENDED_MATCHED_ROUTE_PREREG_20261027.md) remains frozen.

Original contestant ZIPs were independently downloaded, hashed and inspected, not inferred from the prior 75-minute run or the hosted checkpoint JSON:

- V296 pairwise artifact 12703514184: SHA-256 `c0d90c6652deba498c46e6b01e9d3e1ce0317505caf833eea51323b54e6f49a7`
- Fifth-stage-optimized serial artifact 12703682763: SHA-256 `928adb671004dea251dc9c1c558f87a34fc3d3ff233e66d41ddd311d3d305ea4`
- Hosted checkpoint artifact 12703802645: SHA-256 `6686e3a757658c4bc5ed48c644b9e3801f6e1b2ab3c97dfda26a532c5c1e8fff`

The run used the same 3.5 ns target, 2x extracted RC scaling, Nangate45 cells, 260/240 µm die/core floorplan, 0.35 density, and the stronger fifth-stage serial repair. Both contestants reached **complete detailed route (zero DRC)** and produced post-CTS SPEF files and extracted timing reports. No timing guard, electrical guard or physical methodology was relaxed to declare a win.

## Preregistered iteration-3 congestion checkpoint: FAIL

| Metric | Density-0.45 frozen baseline | Density-0.35 matched |
|---|---:|---:|
| V296 candidate DRC, iteration 3 | 12,020 | 3,632 |
| Optimized serial DRC, iteration 3 | 5,281 | 2,119 |
| Candidate/serial normalized ratio | 1.000 | **0.7530548033** |
| Required normalized ratio | — | **<= 0.750000** |

Candidate-only DRC improved **69.7837%**, satisfying the first threshold of <=8,414. However, the *conjunctive* relative-routing criterion failed: 0.7530548033 > 0.75. The missing serial result from the prior experiment is now observed, and it is **2,119**, nine below the preregistered minimum of 2,128 conditional on candidate DRC=3,632. This is a close but real failure; no post-hoc threshold adjustment is permitted.

Both implementations subsequently converged to zero DRC. Candidate required 12 detailed-routing optimization iterations versus 10 for serial; this does not reverse the frozen iteration-3 verdict.

## Extracted-RC physical feasibility: FAIL for both

| Frozen metric | V296 pairwise | Strong serial control | Gate |
|---|---:|---:|---|
| Routed DRC count | 0 | 0 | 0 |
| Extracted cell area (µm²) | 17,213.9245 | 17,994.8998 | <=30,000 |
| Extracted setup slack (ns) | **−0.220829** | **−0.711405** | **>=+0.050** |
| Extracted hold slack (ns) | **−0.010023** | **−0.013032** | **>=0** |
| Capacitance violations | **3** | 0 | 0 |
| Slew violations | 0 | 0 | 0 |

The candidate saves **4.3400% cell area** and leads the serial control by **0.490576 ns of extracted setup slack**, but **neither implementation is timing feasible at the fixed clock**. V296 misses its setup guard by **270.829 ps**, violates hold by **10.023 ps**, and has three capacitance violations. Serial misses its setup guard by 761.405 ps and violates hold by 13.032 ps. The relative slack and area advantages are not GPU speedups, power measurements, or a valid Pareto win between two feasible designs.

## Critical audit interpretation

The generated generic `audit_tile_slice.py` calls the older density-0.45 physical auditor even for the preregistered density-0.35 diagnostic. It consequently returns `Wrong frozen setting V296_PLACE_DENSITY` **after** both OpenROAD runs reach `V296_CTS45_DONE`, complete routing, SPEF extraction and extracted timing. The wrapper reports exit code 3. This is an **auditor scope mismatch**, not an OpenROAD routing or extraction failure. The independent density-aware replay checks original ZIP hashes, physical-input hashes, source RTL provenance, serial fifth-stage marker, exact frozen clock/RC/density markers, completed route, SPEF, setup, hold, area and electrical violations. It does **not** reinterpret the failed feasibility gate as a success.

Reproduction: download the two named GitHub Actions ZIPs and run `python3 research/v296/audit_density035_extracted.py --self-test --candidate pairwise.zip --serial serial.zip`. The exact expected machine-readable result is [preserved here](DENSITY035_EXTENDED_EXTRACTED_PHYSICAL_FALSIFICATION_20261027.json). All prior density-0.45 and density-0.35 artifacts remain unchanged.

## Architectural decision and next boundary

**Reject the decoded density-0.35 V296 physical repair now**, as required by the frozen kill criteria. The relative congestion hypothesis failed narrowly and the candidate failed the much stronger extracted electrical/timing gates. No additional density/time-budget extensions are justified for this repair. Retain V296 as the sole tracked **provisional, physically unvalidated** bank-conflict mechanism; V287 remains retired. A future materially different V296 implementation must preregister its physical hypothesis and equal-resource comparison rather than relabel this failure.

The existing predictive bank-admission laws remain synthetic workload-model results, not architectural novelty or proof of a throughput win. Real trace holdouts remain sealed. Strict equal-consumed-area throughput, bandwidth/port limits, realistic wire/load sensitivity, measured power, and integrated tile consequences are **not established**. Do not claim RTX-5090 equivalence or any feasible GPU speedup.

Kernellum PR #119 and its prospective holdouts are unrelated and must remain untouched.
