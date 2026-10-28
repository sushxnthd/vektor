# V296 integrated-tile repair envelope: clock-only and weak symmetric repairs killed (2026-10-28)

**Evidence tier:** exact fixed-path sensitivity analysis, **not** an RTL repair, new physical experiment, routed signoff, power result, or GPU throughput claim. [Executable independent checker](v296_integrated_repair_kill_envelope.py) uses exact Decimal arithmetic, an independently coded rational threshold oracle, 1-ps brute-force search, and deliberately failing cap/hold negative controls.

## Source and scope

Use only the **integrated** tile-slice routed experiment [Actions #40675850164](https://github.com/sushxnthd/vektor/actions/runs/40675850164), whose original source and limitations are recorded in [the integrated physical falsification](V296_INTEGRATED_TILE_PHYSICAL_GATE_FALSIFICATION_20261028.md). Frozen period 3500 ps, setup guard +250 ps, tile area ceiling 30,000 um2. Do **not** mix the separate D4/D8 deferred-write measurements.

| Integrated physical measurement | V296 | Strong serial |
|---|---:|---:|
| Area (um2) | 17,857.644252 | 18,953.830505 |
| Setup slack (ps) | -1,047.895 | -1,859.922 |
| Hold slack (ps) | -36.622 | -19.796 |
| Max-cap violations | 3 | 3 |
| Feasible | NO | NO |

## Exact necessary recovery law

For contestant i, fixed original setup slack s_i, hold slack h_i, cap count c_i and area a_i, a hypothetical repair with setup recovery u_i, hold recovery v_i, cap fixes k_i, area growth da_i and adverse path migration e_i/f_i can pass the **arithmetic** gate only if:

- u_i >= 250 - s_i + e_i ps;
- v_i >= -h_i + f_i ps;
- k_i >= c_i and a_i + da_i <= 30,000 um2;
- no new slew, DRC, functional, port, occupancy or critical-path failures occur.

Necessary original fixed-path repair thresholds:

| Requirement | V296 | Serial |
|---|---:|---:|
| Setup recovery (ps) | **1,297.895** | **2,109.922** |
| Hold recovery (ps) | **36.622** | **19.796** |
| Cap fixes | 3 | 3 |
| Maximum added area before 30k ceiling (um2) | 12,142.355748 | 11,046.169495 |
| Period needed to pass setup by clock relaxation alone (ps) | 4,797.895 | 5,609.922 |

**Clock-only repair is conclusively insufficient for the measured fixed implementations.** Even a 6,000 ps clock produces positive setup margins but leaves negative hold and three cap violations in both designs. Clock changes cannot be counted as an electrical repair. Conversely, a symmetric +1,500 ps setup-only shift still leaves serial at -359.922 ps setup, below the +250 ps guard, while both retain hold/cap failures.

## Counterfactual stress-test predictions (not measured)

| Equal assumed repair to both | V296 setup / hold (ps) | Serial setup / hold (ps) | Both pass arithmetic gate? |
|---|---:|---:|---|
| 6 ns clock only | +1,452.105 / -36.622 | +640.078 / -19.796 | **NO**, hold and cap |
| +1,500 ps setup only | +452.105 / -36.622 | -359.922 / -19.796 | **NO** |
| +2,200 ps setup, +40 ps hold, fix all 3 caps, +1,000 um2 area each | +1,152.105 / +3.378 | +340.078 / +20.204 | **YES, arithmetic only** |
| Same +2,200 ps setup, +140 ps hold with 100 ps adverse setup and hold migration | +1,052.105 / +3.378 | +240.078 / +20.204 | **NO**, serial misses by 9.922 ps |
| +2,210 ps setup, +140 ps hold, same adverse migration, all caps fixed | +1,062.105 / +3.378 | +250.078 / +20.204 | **YES, arithmetic only** |

The +2.2 ns repair is deliberately **not asserted physically realizable**. A physical design tool must demonstrate the altered critical paths and all electrical checks. Its role here is a stringent numerical falsification boundary, not a design proposal.

## Architectural consequence and kill criterion

Prior exhaustive admission equivalence means V296 and serial admit the same waves at equal clock, latency, occupancy and shared bandwidth. Both integrated implementations fit only **one** slice at the frozen 30k area budget. Thus even if the hypothetical repair closes both at the same 3.5 ns clock, the arbitration-only throughput ratio is **1.000**; energy remains unknown. Any positive result must establish a physically credible frequency, power, or integrated capacity effect with a **feasible matched serial control**. Conditional faster-clock or more-slices scenarios must pay all additional timing, clock-tree, wire, power, area and bandwidth costs.

**Decision:** Keep V296 as the sole *bounded falsification target*, not as a surviving demonstrated mechanism. A single symmetric upstream scheduler-to-operand physical repair trial must recover at least 1.298 ns candidate setup and 2.110 ns serial setup, plus hold and cap closure, without changing the 16-bank/two-read-port/four-slot contract. If it fails, retire V296; do not reopen V287. Preserve the negative results and sealed workload holdouts. Kernellum #119 remains independent and untouched.

No world-class completion claim, RTX-5090 equivalence claim, measured GPU speedup, or power advantage is supported.
