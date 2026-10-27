# V296 deep-bank extracted critical-path replay: frozen protocol (2026-10-28)

**One active mechanism:** V296 pairwise bank admission. V287 remains retired. This protocol is frozen **before opening extracted-RC path reports** from the two completed D4/D8 experiments. It is a read-only reconstruction, not a new route or a matched architecture comparison.

## SHA-verified original evidence

Source: [GitHub Actions #40557136436](https://github.com/sushxnthd/vektor/actions/runs/40557136436). Both original ZIPs were independently downloaded and their hashes, full DEF/SPEF, frozen Tcl/manifest, 3.5 ns clock, 2x RC, 25 ps hold-repair policy, and numerical physical audit were verified locally.

| Original | Artifact | ZIP SHA-256 | Setup | Hold | Final area | Cap violations |
|---|---:|---|---:|---:|---:|---:|
| D8 pairwise | 12769775926 | `92a84c3923eb62cd506241bcb1d8da06cfcfbd6a13328c8e050b14f301086f4b` | -0.684592 ns | +0.010986 ns | 28984.157296 um² | 1 |
| D4 optimized serial | 12769708334 | `edeb136bc054eddf7434119115df198e7d4403c9bd01c0a726df7fb30519755b` | -1.316510 ns | +0.002572 ns | 23265.689819 um² | 6 |

**Both designs fail** the frozen +50 ps final setup guard and zero-capacitance requirement. D4 pairwise and D8 serial timed out, so neither depth has a feasible matched pair. Do not compare D8 pairwise with D4 serial as an architecture advantage.

## Predictions and falsifiers frozen before replay

1. **Topology hypothesis:** the D8 pairwise extracted worst setup path remains primary-input-to-register, as in the pre-CTS path. Evaluate the analogous D4 serial hypothesis independently. If the extracted start/end types differ, falsify this topology hypothesis. Even if it passes, input-to-register topology alone does not prove control-cone locality.
2. **Reproduction:** replay original DEF/SPEF with the existing pinned Nangate45 OpenROAD/LEF/liberty, 3.5 ns clock and IO constraints, and no second RC multiplier. The replayed worst setup and hold slack and each named worst-path slack must match the original within **1 ps**. Missing paths, changed hashes, unsupported commands, or incomplete logs fail closed.
3. **Segment locality:** report startpoint, endpoint, incremental path delays and dominant pins before proposing repairs. OpenSTA increments include upstream interconnect and possibly clock-launch effects; they are not intrinsic gate delays. Any proposed symmetric repair must recover at least **734.592 ps** on D8 pairwise and **1366.510 ps** on D4 serial to reach +50 ps setup. The earlier fixed-effective-path necessary modifiable fractions are 17.555% and 28.371%; actual segment evidence must be used to assess controllability.
4. **Physical kill gate:** unchanged 3.5 ns, 2x extracted RC, equal RF resources, optimized fifth-stage serial, final setup >=+50 ps, hold >=0, zero cap/slew/DRC, area <=30000 um². D8 pairwise has only 1015.843 um² remaining area and one cap failure. A path-only fix cannot pass without electrical closure.

The new experiment must produce read-only named critical paths, SHA-locked original provenance, negative self-tests and complete logs. It must not modify existing artifacts, open workload holdouts, launch another costly full route, claim GPU throughput or RTX-5090 equivalence, or touch Kernellum PR #119.

**Evidence tier:** independently verified original physical observations plus prospectively frozen diagnostic. No extracted path replay result yet.
