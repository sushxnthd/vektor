# V312: frozen mapped-area and zero-wire timing falsification (2026-10-31)

**Decision: KILL the factored V312 RTL implementation.** The matched head-only comparison is a weaker policy comparator, so failing against it is already sufficient to reject this circuit implementation. This does not prove that all bank-aware warp scheduling is impossible, nor does it establish the incremental performance of any equal-information collector.

## Immutable source-pinned evidence
- Source commit: [5542a70](https://github.com/sushxnthd/vektor/commit/5542a70c1b9cd6a6f55c4329f37332f5cc90edae).
- [Hosted run #41182822417](https://github.com/sushxnthd/vektor/actions/runs/41182822417), [raw artifact #13035194090](https://github.com/sushxnthd/vektor/actions/runs/41182822417/artifacts/13035194090).
- Preregistered before measurement: `research/v312/MATCHED_PLACEMENT_RC_PREREG_20261031.md` (commit `fe04ae5`).
- The checker adversarial self-test, pinned container/platform acquisition, and both mapped syntheses completed. The physical workflow failed at candidate dense placement, *before* placement timing and electrical audit. Do **not** call that failure a routed electrical violation.

## Matched Nangate45 typical synthesis and same-netlist zero-wire OpenROAD timing

| Metric | Optimized compact head-only greedy | V312 factored fallback | Candidate/control |
|---|---:|---:|---:|
| Mapped cell area (library units) | 251.370 | 1082.886 | **4.30794x** |
| Zero-wire maximum data arrival | 0.39 ns | 1.68 ns | **4.30769x** |
| 1 ns virtual-clock slack | +0.61 ns | -0.68 ns | not comparable as a speedup |

The **frozen mapped-area ceiling is 1.50x**, violated by a factor of 2.872 relative to that ceiling. The candidate also exceeds the transfer regime's clock-period tolerance by a wide margin. At f=0.5 and G=1.268568, even the optimistic Amdahl upper bound is approximately `1.1184 / 4.30769 = 0.260x` in a controller-clock-limited hypothetical. This is *not* a measured GPU slowdown.

At the 30x30 um frozen dense die, OpenROAD reports candidate placement utilization **201.93%** and `GPL-0301 Utilization exceeds 100%`. This is an expected physical capacity failure of that floorplan, not a synthesis/tooling defect. The compact greedy control placed successfully. No candidate placement-estimated RC, max-cap/slew or routed timing was produced, and the later independent placement audit was correctly skipped.

## Decision and limits

The early synthetic 1.95x admission screen and generic RTL size reduction did not survive matched standard-cell implementation. The candidate is retired under the *precommitted* area kill gate, with no posthoc threshold relaxation. An exploratory finite-queue same-information buffered collector experiment is tracked separately; its independent hosted result must be checked before quoting it as accepted evidence.

V287/V296/V309/V310/V311 remain retired. Keep this PR draft, unmerged, as negative evidence. Do not claim GPU throughput improvement, novel architecture, electrical signoff, or RTX-5090 equivalence. A successor needs a different **single** mechanism and a strong buffered collector baseline before RTL investment.
