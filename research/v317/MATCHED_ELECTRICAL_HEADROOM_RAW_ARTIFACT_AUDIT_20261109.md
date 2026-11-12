# V317 matched electrical-headroom: raw routed artifact audit (2026-11-09 UTC)

**Verdict: NO ELECTRICAL CLOSURE; no positive physical or GPU-throughput claim.**

Source: [GitHub Actions run 42656831972](https://github.com/sushxnthd/vektor/actions/runs/42656831972), source commit `dcb3dc803165a1cdc53440caf16947235a9d6af0`, [artifact 13693891155](https://github.com/sushxnthd/vektor/actions/runs/42656831972/artifacts/13693891155), SHA256 digest `78a16ade7401294c4dde11c4bb5308fb6b3d99d40135422e105739dde5ec7352` (GitHub-reported). Artifact downloaded and its ZIP entries inspected independently. Both `status.txt` records report `exit_code=0`; this is NOT electrical signoff.

Both variants use the same Nangate45/ORFS flow, 300 x 300 um die, 10..290 um core and PLACE_DENSITY_LB_ADDON=0.20. Values below were read from each `reports/nangate45/.../base/6_finish.rpt`, not inferred from workflow success.

| Routed report quantity | Compact | Pairwise |
|---|---:|---:|
| Minimum clock period (ns) | 2.24 | 2.20 |
| Reported fmax (MHz) | 446.10 | 454.59 |
| Setup violation count | 0 | 0 |
| Hold violation count | 0 | **12** |
| Maximum-capacitance violation count | **10** | **13** |
| Maximum-slew violation count | 0 | 0 |
| Maximum-fanout violation count | 0 | 0 |
| Largest listed max-cap excess (report units) | 3.21 | 8.63 |
| Electrical legality | **FAIL** | **FAIL** |

The `5_route_drc.rpt` entries are empty (zero bytes); therefore DRC signoff cannot be inferred from them. No power, integrated GPU IPC, SRAM-macro timing, or matched workload throughput was extracted in this audit. The period/fmax figures are **non-signoff proxies** while max-cap and hold violations remain. Apparent pairwise fmax advantage is not admissible as a validated architectural win.

**Decision:** retain V317/V296 as an electrically unresolved research candidate only; do not claim success, area/clock superiority, or an RTX 5090 comparison. Next experiment must repair both variants under identical constraints, reroute, re-audit zero hold/max-cap/slew/fanout and documented DRC, then evaluate workload service against the strongest physically realizable equal-resource comparator. If legal matched-resource results erase gain, kill the positive mechanism claim. Preserve this negative result without rewriting earlier evidence.
