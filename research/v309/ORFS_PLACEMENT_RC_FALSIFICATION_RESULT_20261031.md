# V309 matched placement-estimated RC: prospective physical no-go (2026-10-31)

**Decision: KILL the factored exact-max four-slot bank-admission RTL for the predeclared clock-limited operating model. Do not silently optimize or replace it.** The single candidate is retired; its draft PR and evidence remain unmerged.

Independent GitHub Actions [#41163708381](https://github.com/sushxnthd/vektor/actions/runs/41163708381) executed both compact-greedy and factored-exact RTL through matched Yosys 0.30+48 Nangate45 synthesis, actual OpenROAD placement at two frozen die/core geometries, placement-estimated metal3 signal parasitics and OpenROAD input-to-output STA. The checker rejected the candidate at the **prospectively frozen** hot2 boundary. [Raw evidence artifact #13027844439](https://github.com/sushxnthd/vektor/actions/runs/41163708381/artifacts/13027844439) contains mapped netlists, placed ODBs, logs, platform file hashes, container digest and independent summary. The CI failure is a **scientific falsification**, not an infrastructure failure.

| Matched geometry | Compact greedy | Factored exact-max | Candidate/base delay | Hot2 ideal issue x frequency upper bound |
|---|---:|---:|---:|---:|
| Dense 30x30 um die | 0.41 ns | 0.47 ns | 1.14634x | 0.95726x |
| Relaxed 45x45 um die | 0.41 ns | 0.48 ns | 1.17073x | 0.93732x |

Frozen hot2 synthetic issue-admission prediction: **1.0973483338585934x**. With controller delay setting the clock, even the *optimistic* admitted-work/frequency product is **below 1** at both placed geometries, before scoreboard, occupancy, control, bank-port and bandwidth costs. Thus it cannot justify a positive clock-limited tile throughput claim under these assumptions. The near-no-win uniform8 regime is still less favorable in issue gain.

## Independent post-kill same-netlist attribution control (2026-10-31)

[GitHub Actions #41164092189](https://github.com/sushxnthd/vektor/actions/runs/41164092189) reran the complete matched placement experiment using a source-pinned Nangate45 platform and a post-hoc **same-netlist zero-wire** STA control. Both controllers were synthesized once each with the same Yosys 0.30+48 and Nangate45 library, then assessed with and without placement-estimated RC in the same OpenROAD 41a51eaf toolchain. [Full raw evidence #13028590141](https://github.com/sushxnthd/vektor/actions/runs/41164092189/artifacts/13028590141).

| Same mapped netlists, same OpenROAD tool | Compact greedy | Factored exact-max | Candidate/base delay |
|---|---:|---:|---:|
| No wire parasitics | 0.39 ns | 0.46 ns | **1.17949x** |
| Dense placed estimated-RC | 0.41 ns | 0.47 ns | **1.14634x** |
| Relaxed placed estimated-RC | 0.41 ns | 0.48 ns | **1.17073x** |

**Causal clarification:** The candidate's timing disadvantage already exists **before wire RC** under this matched synthesis/STA toolchain. Therefore it is incorrect to claim that placement parasitics caused the earlier favorable prelayout result to reverse. The original OpenSTA prelayout 0.45/0.50 ns comparison used different mapping/analysis conditions. This control strengthens the implementation no-go without establishing routed signoff. The hosted workflow intentionally exits nonzero on the frozen clock-limited kill condition.

The mapped standard-cell area premium remains 303.772/251.370 = **1.20847x** (20.85%). An area-delay product proxy under the dense placed condition is approximately **1.385x** compact greedy, but is **not** a measured power or tile-energy ratio. No other architecture was promoted.

---

**Important caveats:** These are *placement-estimated* wire RC, not detailed-routed/extracted parasitics or electrical signoff. The standalone electrical report did not produce machine-readable max-cap/slew violation counts, so do not claim electrical cleanliness. The earlier prelayout comparison used a different Yosys/OpenSTA toolchain and mapped netlists, so the reversal from its favorable delay ratio must **not** be attributed specifically to wire RC without a same-netlist zero-wire control. Placement includes nontrivial site snapping, and fixed small die sizes are stress-test conventions rather than a GPU tile floorplan. A real tile could have slack in the controller path, in which case local delay need not set the global clock. That does not rescue a clock-limited gain or establish any real GPU speedup.

**Research consequence:** Reject the V309 factored exact-max RTL as the active architecture candidate under the frozen model. Retain the valid mathematical equality-partition admission law as a narrow synthetic admission result; do not promote it to a GPU throughput law. A separate future mechanism must be prospectively defined and evaluated against the compact greedy baseline. Preserve V287/V296 no-go evidence. No RTX 5090 equivalence claim.
