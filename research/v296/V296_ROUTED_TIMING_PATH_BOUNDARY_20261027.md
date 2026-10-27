# V296 routed timing failure: independent path-boundary forensics (2026-10-27)

## Scope and evidence tier

This is a **new forensic analysis**, not a new physical implementation, timing closure, or throughput experiment. It independently replays the original completed density-0.35 Actions run [#40427986118](https://github.com/sushxnthd/vektor/actions/runs/40427986118). Original ZIP SHA-256 digests are pinned in [the checker](v296_routed_path_boundary_audit.py), and the checker parses the original OpenROAD logs and synthesized netlists, not previously summarized JSON.

- V296 candidate ZIP artifact 12703514184: c0d90c6652deba498c46e6b01e9d3e1ce0317505caf833eea51323b54e6f49a7
- Strong fifth-stage serial ZIP artifact 12703682763: 928adb671004dea251dc9c1c558f87a34fc3d3ff233e66d41ddd311d3d305ea4
- Both ZIPs include completed detailed routing, extracted SPEF, zero DRC and the original synthesized gate-level netlists. The old flow **did not emit full extracted-RC critical-path traces**. The path-level observations below are from the two **earlier pre-CTS maximum-delay reports per contestant**, and must not be mislabeled as routed critical paths.

## New path-topology finding

The four preserved pre-CTS worst-path reports all end at the **operand-capture register bank** (staged_operand_data). The V296 candidate's two reported paths begin at scheduler round-robin registers candidate.issue.scheduler.rr3[2] and rr3[1], and terminate at staged_operand_data[1][3] and [7][1]. They therefore traverse the scheduler-to-operand-capture cone, not a stand-alone arbiter-only timing path.

| Pre-CTS report | Start → end | Cell instances | Buffer cells | Longest consecutive buffer chain |
|---|---|---:|---:|---:|
| V296 report 1 | scheduler.rr3[2] → staged_operand_data[1][3] | 74 | 32 | **15 buffers, 360.3 ps** cell delay |
| V296 report 2 | scheduler.rr3[1] → staged_operand_data[7][1] | 75 | 32 | **15 buffers, 341.6 ps** cell delay |
| Serial report 1 | wave_valid[23] → staged_operand_data[1][5] | 72 | 18 | 5 buffers, 125.5 ps |
| Serial report 2 | scheduler.rr1[2] → staged_operand_data[1][4] | 72 | 17 | 2 buffers, 68.8 ps |

These are **reported cell delays**, not a removable timing budget. The candidate's 15-buffer chain (wire299/Z through wire275/Z) is a concrete topology to investigate, but changing it may cause other paths to become critical and may worsen slew, capacitance or routing. The sampled paths cannot prove that this chain is the **extracted** critical path.

## Physically measured timing boundary

| Matched density-0.35 metric | V296 | Optimized serial |
|---|---:|---:|
| Post-CTS global-route estimated setup slack | +55.559 ps | −339.133 ps |
| Detailed-route extracted-RC worst setup slack | **−220.829 ps** | **−711.405 ps** |
| Change from global-route estimate to extracted-RC | **−276.388 ps** | **−372.272 ps** |
| Improvement needed to meet frozen +50 ps guard | **270.829 ps** | **761.405 ps** |
| Extracted capacitance violations | 3 | 0 |

The change between global-route and extracted worst slack is a **stage-level difference**, not a decomposition into wire delay, cell delay, clock skew or a particular path: the worst path can change between stages. The V296 implementation additionally has **−10.023 ps hold slack**. Any proposed repair must close setup, hold and all three capacitance violations simultaneously, at the same 3.5 ns clock and 2× RC policy. The serial control must remain independently optimized and equal-resource.

## Falsification of an unsafe diagnosis

The evidence does **not** justify attributing the entire 270.829 ps shortfall to the RF return crossbar, nor claiming that placement density or a 15-buffer-chain edit will recover it. The earlier decoded density-0.35 repair is still **rejected**. The synthetic bank-admission law remains a predictive model for its specified generator, not measured GPU performance.

**Next frozen measurement before further RTL changes:** produce full **post-detailed-route, extracted-SPEF setup and hold path reports for both contestants** with startpoint/endpoint, cells, nets, per-stage arrival, fanout, capacitance, transition and clock skew. Preserve original DEF/SPEF/constraints and verify the reported worst slacks against the existing independent checker. If the extracted critical path is not the scheduler-to-operand-capture cone, reject that repair target. If it is, any new retiming proposal must preserve grants, source-bank snapshots, read-before-write semantics, backpressure, and cycle-accurate useful output; a matched baseline must receive an equivalent pipeline opportunity.

No new V296 implementation is authorized to claim success without a fresh preregistration and full matched physical signoff. V296 is the sole provisional mechanism; V287 retired; Kernellum PR #119 and sealed holdouts untouched.

## Reproduction

Run: python3 research/v296/v296_routed_path_boundary_audit.py --self-test --pairwise pairwise.zip --serial serial.zip

The original ZIPs are downloadable as Actions artifacts 12703514184 and 12703682763. The script rejects modified ZIPs, incomplete physical provenance, missing stage metrics, unexpected path endpoints and extracted timing drift. Local self-test and original-artifact replay passed. Hosted verification of this new checker is not yet established.
