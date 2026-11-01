# V317: prospective integrated 32-wave issue-control routed result (2026-11-02)

## Provenance and exact scope

This evaluates the **previously frozen** protocol in [FROZEN_INTEGRATED_ISSUE_CONTROL_GATE_20261102.md](FROZEN_INTEGRATED_ISSUE_CONTROL_GATE_20261102.md). The matched RTL/physical source SHA is `20c5165651d0a941d3c60f918e4255961b8a2a90`. [Original GitHub Actions run #41352990340](https://github.com/sushxnthd/vektor/actions/runs/41352990340) completed successfully; [immutable 233-file artifact #13101813367](https://github.com/sushxnthd/vektor/actions/runs/41352990340/artifacts/13101813367) contains both source and pairwise ORFS results. Official ORFS image was pinned to `sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8`.

Matched design: source 32-wave steal scheduler, 32-way bank selection mux, RF bank arbitration and acceptance feedback, matched 356 sequential cells, input/output registers, Nangate45 typical, 120 x 120 um die, 112 x 112 um core, 2.0 ns clock target, 10 fF outputs, extracted RC, same RTL except fixed-priority bank arbiter implementation. **No RF SRAM macro, datapath, RF port replication, or workload switching.** The source and pairwise RTL passed 4,096-cycle source-faithful equivalence, 13,153 accepted events in the test.

A read-only [independent audit script](rtl/audit_integrated_issue_route.py) recomputes the metrics from the original raw ZIP, checks source and container provenance, all route exit codes, RTL regression, extracted RC, DRC/antenna, setup/hold and electrical reports. It was tested locally against the original ZIP. The [separate hosted audit](../../.github/workflows/v317-integrated-issue-evidence-audit.yml) is a new reproduction gate; **do not mark hosted audit passed before inspecting its result**.

## Integrated routed measurements (raw final OpenROAD reports)

| Metric | Source bank-mask | Pairwise bank-credit |
|---|---:|---:|
| Final std-cell area (um2) | 7386.29 | **6599.46** |
| Routed wire length (um) | 56255 | **53447** |
| Extracted-RC Fmax (MHz) | 496.635 | **516.921** |
| Extracted-RC minimum period (ns) | 2.013551 | **1.934532** |
| Setup worst slack at 2 ns (ns) | **-0.013550** | **+0.065469** |
| Setup-violating paths | **12** | **0** |
| Hold worst slack (ns) | +0.015800 | +0.014991 |
| Max slew/cap/fanout violations | 0/0/0 | 0/0/0 |
| Final detailed-route DRC | 0 | 0 |
| Antenna net/pin violations | 0/0 | 0/0 |
| Default-activity power estimate (mW) | 5.49986 | **5.19150** |
| Extracted nets | 6828 | 6378 |
| SRAM macro area (um2) | 0 | 0 |

**Derived from raw artifact:** pairwise saves 786.83 um2 (**10.653%**) of integrated standard-cell area, 2808 um (**4.992%**) of routed wire length, and 0.30836 mW (**5.607%**) of default-activity power proxy. The final reported Fmax improves **4.085%**, not the isolated arbiter's 2.66x period ratio. The integrated setup slack difference is **79.0193 ps**.

**Decisive timing nuance:** the source implementation routes successfully and passes reported DRC, antenna, slew, capacitance, fanout and hold checks, but **fails the 2.0 ns setup gate (12 paths, -13.55 ps)**. The pairwise implementation passes this specific setup gate (+65.47 ps). It is incorrect to say both have clean timing. The source may be recoverable through timing repair, seed search or extra area; that stronger equal-resource legal baseline has NOT yet been evaluated. The observed worst register-to-register timing path runs through scheduler round-robin state (rr1 to rr0) in both variants, not necessarily the bank arbiter itself. Physical placement changes could contribute to the difference.

## Frozen prediction adjudication

- **P1 PASS in tested simulation:** 4096-cycle integrated equivalence with 13,153 accepted events. Not a formal proof for all states.
- **P2 PASS:** integrated mapped/routed area advantage survives the scheduler and bank mux. This is much smaller in percentage terms than the isolated control-block area reduction.
- **P3 PASS as a caution against extrapolation:** actual integrated Fmax ratio is 1.04085x; **the isolated 2.66x timing ratio does not transfer**. The original 2.0-ns setup gate fails; pairwise passes. Do not call the original timing-clean.
- **P4 PASS as semantic no-IPC control:** both variants produce the same accepted grants at equal clock and RF ports. Any performance difference must arise from a realizable tile clock, capacity or power-budget consequence, not an intrinsic service-rate change.

## Positive boundary and falsification

For fixed tile area budget B, other tile area A_other, implementation area A_issue,x, shared bandwidth C, workload offered rate L, tile service r and actual integrated clock T_x:

`N_x = floor(B/(A_other+A_issue,x))`

`R_x = min(L, C, N_x*r/T_x)`

`G = R_pairwise / R_source`.

This is a **conditional resource accounting law**, not a novel GPU scheduling law. If both fit the same tile count, operate at the same clock and share the same port/bandwidth ceiling, **G=1**. If both are bandwidth-bound, **G=1** even when the optimized controller is smaller. For a fixed 2-ns clock at the tested corner, the source violates setup while pairwise passes; this alone does not prove a real tile can run faster.

The measured pairwise **+65.4692 ps setup margin** is a single-corner *local* adverse-delay budget before it also fails the 2-ns gate. The original needs at least 13.5501 ps of setup repair to close 2 ns, ignoring changes to uncertainty and placement. Differential timing shifts of 79.0193 ps would erase the observed setup-slack advantage under otherwise fixed conditions. These are deterministic margins from the reports, **not extracted wire-load or PVT sensitivity experiments**.

## Research decision and next kill gate

**Retain pairwise fixed-priority bank-credit as a single-corner, physically routed, grant-equivalent issue-control optimization.** It is not yet a proven GPU architecture throughput result.

**Highest priority next experiment:** preregister and run a strongest equal-resource source control with legal timing repair (resizing/buffering and multiple placement seeds) at 2 ns, then a paired source/pairwise route with the same actual RF SRAM macros and port loads, representative issue traffic and activity-derived power. Compare feasible tile clocks and tile area/power, including a bandwidth-saturated no-win regime. Run at multiple corners or explicit RC/clock uncertainty margins. If legal optimized source closes 2 ns at comparable area/power or the real tile critical path/bandwidth is unchanged, **kill the GPU throughput claim** and retain only a controller implementation result.

No RTX-5090-equivalence or measured GPU IPC claims are supported. Kernellum PR #119 remains a separate untouched workstream.
