# V296 third-round prospective physical-closure result — 2026-10-23

## Immutable experiment identity

- Frozen **before execution**: `THIRD_ROUND_SYMMETRIC_CLOSURE_PREREG_20261023.md`; the two-round experiment remains **FROZEN_GATE_FAIL**, unchanged.
- Mechanism: **V296 pairwise RF-bank conflict admission**, sole active candidate. V287 retired. Branch: `research/v296-pairwise-bank-conflict`; draft PR #13.
- GitHub Actions [run 39976579976](https://github.com/sushxnthd/vektor/actions/runs/39976579976), successful `physical` job 120492634866; immutable [53-file evidence artifact 12510864875](https://github.com/sushxnthd/vektor/actions/runs/39976579976/artifacts/12510864875); archive SHA-256 `0cc1c3904851442265f07c34de1c278a53da3d96a760e9d35a240332c2fe1060`. Source commit `3f31111913c7fb19b73abdaa05acc7cad0b707bb`.
- Independent fail-closed audit: `python3 research/v296/audit_third_repair.py build/v296/third`. CI reported `THIRD_AUDIT_SELFTEST_PASS` and `THIRD_PROVISIONAL_GLOBAL_ROUTE_PASS`.
- Tooling: pinned OpenROAD 2024-12-14 release, Ubuntu 22.04 Yosys, pinned Nangate45 models, matched 140 × 140 µm die / 120 × 120 µm core, 3.5 ns common clock, 0.005 pF output load, two RC settings, same three repair rounds for all architectures.

## Prospective six-case results (after third repair and global routing)

| RC | Variant | Cell area (µm²) | Setup slack at 3.5 ns (ns) | Max-slew | Max-cap |
|---|---|---:|---:|---:|---:|
| Nominal (1×) | Original | 6400.758 | +0.004180 | 0 | 0 |
| Nominal (1×) | Optimized one-hot | 6249.936 | +0.360324 | 0 | 0 |
| Nominal (1×) | **V296** | **5370.806** | **+0.762884** | **0** | **0** |
| High (2×) | Original | 7175.616 | +0.113725 | 0 | 0 |
| High (2×) | Optimized one-hot | 6939.142 | +0.179987 | 0 | 0 |
| High (2×) | **V296** | **5985.266** | **+0.678807** | **0** | **0** |

All six meet the frozen nonnegative setup and zero-slew/zero-cap predicates at 3.5 ns **under global-route RC estimates**. V296 beats both controls on mapped postrepair controller area and modeled setup slack in both conditions.

The preregistered quantitative predictions were also supported:
- **Nominal**: V296 14.0662% smaller than smallest control, +0.402560 ns setup-slack lead over fastest control. Frozen thresholds ≥10% and ≥0.30 ns.
- **High RC**: V296 13.7463% smaller, +0.498820 ns lead. Both thresholds met.
- Third repair fixed the previously failed original-control nominal setup constraint (−0.039100 ns after two rounds to +0.004180 ns after three), but **4.18 ps is not a robust guardband**. This is a *new* pass; it does not retroactively turn the previous two-round failure into a pass.

## Scientific interpretation and hard limitations

**Outcome: provisional global-route physical closure only.** This is a meaningful relative controller-area result under matched implementation effort, **not** final silicon physical closure. It does not include clock-tree synthesis, hold checks, detailed-route DRC, post-route extracted SPEF, dynamic power, IR/EM, equal-area optimized alternative, integrated tile throughput, or silicon measurement. The 3.5 ns clock is a **shared analysis constraint**, not validated GPU operating frequency.

Functional equivalence predicts **zero same-clock instructions-per-cycle gain** for V296 versus controls. Controller area advantage is not GPU area advantage. A conservative algebraic tile-density consequence, if the optimized controller consumes fraction `a` of a fixed tile and all else stays unchanged, is `A_tile,new/A_tile,control = 1 - 0.140662 a` at nominal RC; this is **not** a measured tile integration or throughput result. For example `a=0.05` implies ~0.703% tile-area reduction *under these assumptions*, not 14%.

The nominal original-control +4.18 ps setup margin makes post-route/clock-tree validation especially important. Do not claim V296 passes detailed physical signoff, 5090-equivalence, frequency improvement or world-class completion.

## Next kill gate (must be frozen before evaluation)

Use the same three designs, both RC regimes, same 3.5 ns clock and output loads. Route all six with a pinned detailed router; produce full DRC reports, physically routed DEFs, calibrated Nangate45 OpenRCX extraction rules and nonempty extracted SPEF; recheck setup, **hold**, slew and capacitance with extracted parasitics. Fail closed on missing technology calibration, unsupported commands, route/DRC errors, timing violations, or V296 loss of area/timing advantage. Compare strongest optimized control after equal repair and, separately, an **equal-tile-resource** control. Keep workload holdouts sealed until physical and matched-resource gates pass. Preserve all negative evidence.

**Research decision:** V296 survives as the sole provisional mechanism. No merge. Kernellum remains separate.
