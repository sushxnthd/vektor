# V296 extracted cap-locality falsification: repeated routed candidate (2026-10-26)

**Evidence tier:** original GitHub Actions post-CTS propagated-clock, detailed-route OpenRCX artifact, Nangate45, 2x extracted RC. **Not signoff and not a GPU tile.** This analysis is a new independent *net-topology and geometry* audit of the physical artifact, not a new architecture mechanism. V296 remains the sole provisional candidate; V287 remains retired.

## Provenance and reproducibility

- [Physical experiment 40309580865](https://github.com/sushxnthd/vektor/actions/runs/40309580865), pairwise job 121527810665, artifact 12648648864.
- Original ZIP SHA-256: `057d4fe6d4bf67164857c54c9635c302e163da6b486f59515b7b8151578d8388`.
- Independent checker: `python3 research/v296/extracted_cap_locality_independent_audit.py --self-test --zip path/to/v296-tile-slice-pairwise.zip --output /tmp/v296-cap.json`. Local checker and adversarial corrupted-input test passed. The checker reads original OpenROAD report, detailed-route SPEF, placed DEF and physical audit JSON, rather than treating the console summary as independent evidence.
- Machine-readable observations: `research/v296/EXTRACTED_CAP_LOCALITY_RESULT_20261026.json`. No original artifacts or prior evidence were rewritten.
- This run repeats the original candidate physical implementation and its negative timing/electrical result. It is **not an independent silicon sample** and does not imply statistical reproducibility over seeds. The paired serial rerun was still in progress when this report was frozen; the earlier completed matched serial experiment already failed its physical gate.

## Hard physical result

| Gate / metric | Routed V296 observation | Decision |
| --- | ---: | --- |
| Detailed-route DRC count | 0 | DRC-only pass |
| Worst extracted setup slack | **-1.047895 ns** | FAIL |
| Required setup guard | +0.050 ns | Missing **1.097895 ns** |
| Worst extracted hold slack | **-0.036622 ns** | FAIL by **36.622 ps** |
| Max-slew violations | 0 | Pass at this tier |
| Max-capacitance violations | **3** | FAIL |
| Final cell area | 17,857.644252 µm² | Not equal-consumed-area comparison |

The physical result reproduces the earlier matched integrated-slice candidate observation; the 3.5 ns clock does not close. No achieved Fmax, dynamic power, GPU throughput or RTX-5090 equivalence is inferred. Fixing the three capacitance checks alone would not remove the >1 ns setup deficit or hold violation.

## New physical diagnosis: all three cap violations are *point-to-point*

The independent parser maps STA driver pins to SPEF connectivity and physical DEF cell placements, using the DEF scale of 2,000 database units per micrometre.

| STA driver | Physical sink | STA cap / limit (fF) | Excess | SPEF net cap (fF) | DEF cell-origin Manhattan separation |
| --- | --- | ---: | ---: | ---: | ---: |
| `_12573_/ZN` (OAI33_X1) | `_12575_/A` (MUX2_X1) | 13.085626 / 11.482200 | **+13.96%** | 12.1392 | **37.97 µm** |
| `_10310_/ZN` (OAI33_X1) | `wire100/A` (BUF_X2) | 12.548141 / 11.482200 | **+9.28%** | 10.7689 | **34.93 µm** |
| `_09621_/ZN` (AOI222_X2) | `wire106/A` (BUF_X4) | 26.040531 / 25.634800 | **+1.58%** | 22.6387 | **76.25 µm** |

Each violating SPEF net has exactly two connected cell pins: **one driver and one sink**. These are not high-fanout violations. Two sinks are physical buffers inserted by the backend, and the third is a MUX. The distances above are **cell-origin Manhattan separations**, not actual wire lengths or independently measured RC delay. SPEF net total capacitance is not numerically identical to STA pin load; the checker intentionally reports both without equating them.

This falsifies a simplistic diagnosis that the three remaining capacitance violations are caused by broad fanout. A localized placement/buffering or driver-size investigation is more appropriate. It does **not** establish whether wire, pin capacitance, routing detour, or sizing is the dominant causal source. In particular, rebuffering can worsen setup timing, so cap-only repair is not automatically beneficial.

## Decisive next physical experiment

1. Preserve the same 3.5 ns clock, original guard, RF resources, load model, and strongest serial control. Diagnose extracted setup/hold endpoints **in addition** to these three local cap nets; do not infer that the cap violators lie on the critical setup path.
2. Freeze a symmetric physical intervention before evaluating: placement locality / bounded buffering or cell sizing for both contestants. Report exact modifications and resulting area, setup, hold, cap, slew, DRC and RC sensitivity.
3. Independently audit both completed artifacts, including the optimized fifth-stage serial alternative. Reject the V296 integrated-performance claim if candidate cannot close all gates or if an equal-resource serial implementation matches it. Only then proceed to workload and prospective holdout claims.

**Decision:** V296 integrated physical feasibility **fails** on the completed routed candidate. Its hypothetical area-packing wins cannot be promoted to GPU performance while the physical gate is red. No new mechanism is introduced. Kernellum PR #119 and prospective holdouts are untouched.
