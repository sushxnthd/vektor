# V296 six-case extracted-RC falsification and electrical-risk boundary (2026-10-24)

**Evidence tier:** completed GitHub Actions detailed-route/OpenRCX run 39995731088, artifact 12523741140, independently parsed by the frozen `research/v296/audit_detailed_route.py` checker. **Frozen 3.5 ns all-six gate: FAIL.** This document preserves the failed result without relaxing thresholds or opening workload holdouts.

## Provenance

- Run: https://github.com/sushxnthd/vektor/actions/runs/39995731088
- Raw 71-file artifact: https://github.com/sushxnthd/vektor/actions/runs/39995731088/artifacts/12523741140
- Workflow head: `624b967c2c2093b32b5841e9c5ffc105377bf159`.
- Toolchain: pinned Nangate45 research technology, OpenROAD detailed route, OpenRCX SPEF extraction; *not* foundry signoff. Clock ideal/pre-CTS.
- Frozen decision from independent checker: `DETAILED_PHYSICAL_GATE_FAIL`; `quantitative_prediction_supported=true`, `all_clean=false`, `all_timed=false`, `all_smaller=true`, `all_faster=true`.

## All six measured implementations

| RC | Implementation | Cell area (um2) | Extracted setup slack (ns) | Extracted hold slack (ns) | Max-slew violations | Max-cap violations | Router DRC |
|---|---|---:|---:|---:|---:|---:|---:|
| nominal | original | 6400.758146 | -0.051866 | +0.242990 | 0 | 0 | 0 |
| nominal | optimized | 6249.936124 | +0.284155 | +0.246046 | 0 | 0 | 0 |
| nominal | V296 | 5370.806022 | +0.683897 | +0.259154 | 0 | 0 | 0 |
| high | original | 7175.616101 | -0.159637 | +0.251041 | 0 | 0 | 0 |
| high | optimized | 6939.142150 | -0.179354 | +0.268246 | 0 | 0 | 0 |
| high | V296 | 5985.266061 | +0.361922 | +0.283003 | **33** | 0 | 0 |

The optimized control is the strongest *area* control in both scenarios. The strongest *setup* control is optimized at nominal RC (+0.284155 ns), but original at high RC (-0.159637 ns); use the maximum of both controls for timing dominance.

## What survives, what fails

- V296 retains **14.0662%** nominal and **13.7463%** high-RC controller cell-area savings against the smaller control.
- V296 extracted setup lead over the fastest control is **+0.399742 ns** nominal and **+0.521559 ns** high RC. The earlier prospective +0.20 ns and >=10% quantitative relative predictions survive.
- All six have zero router DRC, nonnegative extracted hold slack, and zero maximum-capacitance violations.
- The original control misses 3.5 ns setup in both regimes; the optimized control additionally misses setup at high RC. **V296 has 33 high-RC maximum-slew violations**, despite positive setup slack. Thus the frozen all-six clean-and-timed gate fails for multiple independent reasons. Positive setup slack cannot excuse max-slew violations.
- The 33 count is a report count, **not** a claim of 33 distinct repairable nets or proof of root cause. Endpoint attribution requires the detailed report and targeted extraction.
- Relative controller-level dominance does **not** demonstrate same-clock IPC improvement (predicted 0%), GPU frequency gain, tile-level PPA, or architecture novelty.

## Prospective repair-loss and equal-resource falsifiers

Use the **measured extracted** metrics as the reference; do not retroactively apply the earlier global-route budget as if it were measured extracted timing. Let `a_p,a_o` be *additional* post-extraction repair area for V296 and optimized control and `l_p,l_c` be *additional* setup-slack loss for V296 and the strongest control. No new numbers below are measured repairs.

- For nominal RC, a V296-only repair with optimized control unchanged preserves >=10% area savings if `a_p <= 254.136490 um2`. It preserves >=+0.20 ns setup lead if `l_p <= 0.199742 ns`, and setup closure if `l_p <= 0.683897 ns`.
- For high RC, a V296-only repair with optimized control unchanged preserves >=10% area savings if `a_p <= 259.961874 um2`. It preserves >=+0.20 ns setup lead against the **currently fastest original control** if `l_p <= 0.321559 ns`, and setup closure if `l_p <= 0.361922 ns`. Comparing only against optimized high gives a misleadingly looser +0.541276 ns lead; **use the strongest of both controls**.
- If controls also receive repair, the exact area condition is `a_p - 0.9*a_o <= 0.9*A_o - A_p`, and the exact timing condition is `l_p - l_c <= (S_p-S_c)-0.20 ns` for the relevant strongest control; the identity of the strongest control can change after optimization. Recompute both controls, not a fixed one.
- **V296**, not the optimized control, has **879.130102 um2 nominal / 953.876089 um2 high** of area headroom before reaching the optimized control's current area. The optimized control already uses more area. An equal-resource Pareto test must use a **common area ceiling** (at least the larger existing implementation, or a separately frozen tile envelope), allow *both* designs independent timing/area optimization under that ceiling, and compare achieved PPA. The control's best attainable slack at that common ceiling is **unmeasured**. Equal repair iteration counts do not establish an equal-resource Pareto win.
- A targeted V296 slew repair that sacrifices the relative advantage, or an equal-area optimized control that erases it, triggers the previously frozen retirement criterion. Do not rescue by changing the clock or selectively weakening RC/loads.

## Decisive next physical experiment (new protocol; does not relabel this failed run)

1. Inspect extracted high-RC V296 slew-violating endpoints, net fanout and buffer chain to identify whether 33 reported violations cluster on shared nets. Preserve endpoint tables and raw OpenSTA output.
2. Freeze **before evaluation** a matched post-route electrical repair procedure with the same max-slew/cap/hold/setup constraints and equal repair access for both controls and V296. Preserve detailed-route DRC, extracted SPEF, netlist, DEF, cell-area delta and timing delta for each.
3. Optimize the strongest control independently within **the same total controller area as the repaired V296** (and, ultimately, the same tile budget). Compare Pareto envelopes rather than only equal iteration counts.
4. Require V296 to close max-slew, max-cap, setup and hold with DRC=0, while retaining strictly better area and extracted timing than the best equal-resource alternative. If not, retire. **Do not** claim the original frozen all-six gate passed.
5. Only after physical survival, perform CTS/post-CTS hold and power proxies, tile critical-path/bandwidth modeling and prospective unseen workload tests. Keep existing workload holdouts sealed.

**Scientific status:** promising physically extracted *controller* implementation topology, but a **failed physical gate**, not a GPU architecture breakthrough. V287 remains retired. Kernellum PR #119 is separate.
