# V296 post-CTS 40%-slew intervention falsified; prospective fanout-16 repair protocol (2026-10-24)

## Evidence tier and immutable negative result

The sole active Vektor mechanism remains **V296 pairwise RF-bank conflict admission**; V287 is retired. The previous preregistered symmetric 40%-slew-margin experiment is complete: [run 40100763112](https://github.com/sushxnthd/vektor/actions/runs/40100763112), tested commit `dd5c279792b229a16aca92bc2f5a8490520d6c01`. This is post-CTS propagated-clock, detailed-route OpenRCX at 45% placement target, 3.5 ns, 2x extracted RC, Nangate45, and identical 7,400 um^2 area ceiling; **not foundry signoff**. Both contestant jobs completed; the aggregate deliberately returned failure.

| Metric | V296 10% prior | V296 40% new | Serial 10% prior | Serial 40% new |
|---|---:|---:|---:|---:|
| Final area (um^2) | 5989.256202 | 5989.256202 | 6953.771781 | 6953.771781 |
| Extracted setup (ns) | +0.299279 | +0.299279 | -0.188049 | -0.188049 |
| Extracted hold (ns) | +0.286195 | +0.286195 | +0.271676 | +0.271676 |
| Max-slew violators | 32 | 32 | 0 | 0 |
| Max-cap violators | 0 | 0 | 0 | 0 |

All displayed physical metrics are identical to reported precision. The 40%-margin intervention **failed to change the measured result**. The 32 V296 violating endpoints still belong to `issue_wave0[0]`, with 79 internal sinks, 0.126904 pF SPEF net capacitance and 272.569 ps worst transition against a 250 ps limit. This is a *null intervention*, not a near-pass, and not proof that the tool did nothing internally. Original 40%-run artifact SHA-256: pairwise `137ea9eada5033f21baa122bded96b9f6a5569a77f432842cd98537c435eb7b1`, serial `4ffefa72e76a8f64799c38c27ad68ba25f3d1eb980c4bc6982759321a0423cb7`, aggregate `e091749ade719ba62cc05c35c08a19c00e655c54c70df024e8e9f23adea6db2c` (digests recorded by Actions; not independently rehashed in this run). Prior 10% source: [CTS45 single-net falsification](CTS45_SLEW_SINGLE_NET_FALSIFICATION_20261024.md).

**Decision: KILL 40%-SLEW-MARGIN POLICY as a sufficient repair.** V296 architecture itself remains provisional. Neither contestant passes the physical gate; no feasible-control Pareto win or GPU throughput gain exists.

## Prospective next experiment: fixed symmetric fanout-16 intervention

This protocol is frozen before new fanout-16 physical outcomes. OpenROAD's [gate-resizer documentation](https://openroad.readthedocs.io/en/latest/main/src/rsz/README.html) states that `repair_design` addresses max fanout and that `set_max_fanout` can constrain fanout. A separate [OpenROAD issue](https://github.com/The-OpenROAD-Project/OpenROAD/issues/1736) documents the important caveat that Liberty `fanout_load` attributes may make fanout constraints ineffective. Therefore, this is a falsifiable hypothesis, not a guaranteed repair.

**Only new physical intervention** relative to the completed 40% run: after CTS and placement parasitic estimation, set `set_max_fanout 16 [current_design]` immediately before the existing `repair_design -cap_margin 20 -slew_margin 40`. Apply it identically to pairwise and serial-onehot. No changes to RTL, port loads, 250 ps transition limit, geometry, 3.5 ns clock, RC, CTS, setup/hold repair, detailed route, SPEF, or the control's extra fifth pre-CTS repair. The 40%-margin result is historical; this new experiment is *not* an independent holdout for the earlier single-net observation.

### Frozen predictions and decision rules

1. **Topology prediction:** candidate output-port net `issue_wave0[0]` has at most 16 internal sinks after extracted routing, compared with the prior 79. Report exact extracted output-net fanout for both variants and fail closed if the port is missing or SPEF connectivity is ambiguous. If the limit has no observable effect, classify as a fanout-policy null intervention; do not re-tune.
2. **Candidate physical gate:** complete detailed route and SPEF, new clock buffers, area <= 7400 um^2, extracted setup >= +0.050 ns, hold >= 0, zero max-slew/max-cap and routing DRC violations. A topology improvement without electrical closure is a **FAIL**.
3. **Matched-control Pareto gate:** both contestants physically feasible, candidate area saving >= 10% and setup lead >= +0.200 ns. If the control remains setup-infeasible, report **NO PARETO CLAIM**, even if the candidate closes.
4. **Area/timing repair budget:** at the historical control area the candidate may grow by at most 269.138 um^2 before losing the 10% area advantage, and differential setup degradation may not exceed 287.328 ps before losing the 200 ps lead. Recompute from *new* matched measurements, never use these historical budgets as a pass.
5. **Negative/indeterminate handling:** preserve raw logs, DEF, SPEF, DRC, independent per-net checker and all failures. No output-interface relaxation, selective candidate-only repair, control weakening, or changing frozen predictions. A physical win does not establish strict equal-consumed-area, power signoff, prospective workload speedup or RTX-5090 equivalence.

## Architectural boundary

V296 and serial one-hot have equivalent admission semantics. At fixed frequency and equal resources, the admitted operations/cycle gain is zero. A future integrated tile must separately demonstrate whether improved controller timing or area alters tile clock/resource bottlenecks while preserving bandwidth, occupancy and power limits. Keep unseen workload regimes sealed until that model is frozen.
