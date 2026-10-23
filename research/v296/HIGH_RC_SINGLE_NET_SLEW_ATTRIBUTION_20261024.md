# V296 high-RC electrical failure localized to one extracted net (2026-10-24)

**Evidence tier:** completed pinned OpenROAD **read-only extracted-SPEF replay**, independently audited, [workflow 40018972185](https://github.com/sushxnthd/vektor/actions/runs/40018972185), [artifact 12529407452](https://github.com/sushxnthd/vektor/actions/runs/40018972185/artifacts/12529407452). Source physical artifact: [run 39995731088](https://github.com/sushxnthd/vektor/actions/runs/39995731088/artifacts/12523741140). **Post-hoc endpoint attribution, not a prospective repair or physical-gate pass.**

## Reproduced immutable physical metrics

The independent checker returned `SLEW_FORENSICS_REPLAY_PASS`, matching the original high-RC V296 design with **zero input DEF/SPEF/netlist hash changes**.

| Metric | Frozen original | Independent replay |
|---|---:|---:|
| Controller area (um2) | 5985.266061 | 5985.266 |
| Extracted setup slack (ns) | +0.361922 | +0.361922 |
| Extracted hold slack (ns) | +0.283003 | +0.283003 |
| Maximum-slew violations | **33** | **33** |
| Maximum-capacitance violations | 0 | 0 |
| Detailed-router DRC | 0 | Not rerun; original route reported 0 |

The replay itself performs no new routing or electrical repair. The original six-case detailed physical gate remains **FAILED**.

## Exact violating-pin attribution

The 33 violating entries in `replay.slew.txt` were joined to the immutable `pairwise.high.detail.spef` `*NAME_MAP`, `*D_NET`, and `*CONN` records. **All 33 violations map to the single routed net `issue_wave0[0]`.** The entries comprise **32 cell input pins and one top-level output port**.

| Property of `issue_wave0[0]` | Extracted evidence |
|---|---:|
| Distinct violating nets | **1** |
| Violating pin entries on this net | **33** |
| Total cell-input connections on net | **79** |
| SPEF declared net capacitance | **0.127312 pF** |
| Output driver | **INV_X32** |
| Frozen max-transition constraint | **0.250000 ns** |
| Worst observed transition | **0.281187 ns** |
| Worst transition excess | **31.187 ps** |

The worst violating endpoint is the output port `issue_wave0[0]`; other violating pins include `_5038_/S`, `_4933_/S`, and `_5012_/A2`. These names and the 33-entry report are preserved verbatim in the raw artifact.

This **confirms the preregistered load-concentration hypothesis** from `EXTRACTED_SPEF_LOAD_CONCENTRATION_20261024.md` for this particular high-RC implementation. It does **not** establish that the net can be repaired within the area/timing budgets or that the mechanism is novel.

## Decisive bounded next experiment

1. Freeze a targeted **single-net** fanout/buffer or placement strategy for `issue_wave0[0]` before measuring repaired PPA; do not alter global max-slew, capacitance, RC, clock, or output-load constraints.
2. Preserve an independent optimized-control timing/area Pareto search under a **common area ceiling**. Equal repair counts alone are insufficient.
3. Require zero slew/cap violations, zero detailed-route DRC, nonnegative extracted setup/hold, and retained V296 area/timing dominance against the **best equal-resource control**.
4. The V296-only high-RC repair may add **at most 259.961874 um2** if the optimized control remains unchanged and V296 is to retain >=10% area savings. It may lose **at most 0.321559 ns** setup slack to preserve the frozen +0.20 ns lead against the *currently fastest* high-RC control, and **at most 0.361922 ns** to retain 3.5 ns setup closure. These are conditional budgets, not measured repair costs.
5. If the one-net repair or stronger equal-resource control erases the advantage, retire V296. Do not reinterpret the previously failed six-case gate as passed.

**Limits:** No CTS, signoff, dynamic power, GPU IPC gain, tile throughput, unseen workload result, or RTX-5090-equivalence claim. Workload holdouts remain sealed. V287 remains retired.
