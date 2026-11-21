# V317: matched timing-oriented synthesis challenger falsifies the repair hypothesis (2026-11-02)

## Immutable inputs and preregistration
This adjudicates [FROZEN_INTEGRATED_TIMING_BASELINE_CHALLENGE_20261102.md](FROZEN_INTEGRATED_TIMING_BASELINE_CHALLENGE_20261102.md), committed before the challenger ran. Source is the original 32-wave integrated issue-control block; candidate is the same 356-flop scheduler, mux, register boundaries and acceptance feedback with only the bank arbiter changed. No SRAM, RF datapath or additional ports.

- Area-oriented ABC baseline: [run 41352990340](https://github.com/sushxnthd/vektor/actions/runs/41352990340), [raw artifact 13101813367](https://github.com/sushxnthd/vektor/actions/runs/41352990340/artifacts/13101813367), SHA `20c5165651d0a941d3c60f918e4255961b8a2a90`.
- Speed-oriented ABC challenger: [run 41354169431](https://github.com/sushxnthd/vektor/actions/runs/41354169431), [raw artifact 13103687465](https://github.com/sushxnthd/vektor/actions/runs/41354169431/artifacts/13103687465), SHA `cac1d1185ee77179257b451805df7b65c664eafb`.
- Pinned official ORFS image: `openroad/orfs@sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8`. Identical Nangate45 typical, 120 x 120 um die, 112 x 112 um core, 2 ns target, 10 fF outputs, extracted RC.
- GitHub comparison of the two source SHAs confirms **no RTL or constraint changes**; only audit/report/workflow files were added.
- The actual Yosys mapping logs explicitly invoke `abc_area.script` for the original experiment and `abc_speed.script` for the challenger. Thus `ABC_AREA=0` was honored, not silently ignored.
- Both artifacts report the same 4,096-cycle RTL equivalence pass with 13,153 accepted events. Both completed detailed routing with final DRC 0 and antenna net/pin violations 0.

## Physical outcome

| Routed measurement | Area ABC, source | Area ABC, pairwise | Speed ABC, source | Speed ABC, pairwise |
|---|---:|---:|---:|---:|
| Standard-cell area (um2) | 7,386.29 | 6,599.46 | 11,826.40 | 8,741.29 |
| Fmax (MHz) | 496.635 | 516.921 | 378.804 | 496.741 |
| Setup worst slack at 2 ns (ps) | -13.550 | +65.469 | **-639.889** | **-13.122** |
| Setup-violating paths | 12 | 0 | **15** | **12** |
| Hold worst slack (ps) | +15.800 | +14.991 | **-13.648** | +3.995 |
| Hold-violating paths | 0 | 0 | **22** | 0 |
| Max-cap violations | 0 | 0 | **2** | 0 |
| Max-slew / max-fanout violations | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Routed wire length (um) | 56,255 | 53,447 | 161,831 | 74,721 |
| Default-activity power proxy (mW) | 5.500 | 5.192 | 9.500 | 6.726 |
| Timing-repair buffers | 1,352 | 1,060 | 3,626 | 2,182 |
| Final routing DRC | 0 | 0 | 0 | 0 |

**The speed-oriented source is not timing/electrically legal at 2 ns** despite successful route: setup, hold and max-cap fail. The speed-oriented pairwise is also **not timing-legal at 2 ns** because setup fails. Routing success must not be conflated with signoff.

Relative to its own area-oriented mapping, the speed-oriented source gains **60.11% area**, **187.67% wire**, and **72.74% default-activity power**, while Fmax *falls* **23.73%** and setup slack worsens **626.34 ps**. Speed-oriented pairwise gains **32.45% area**, **39.80% wire** and **29.56% power**, while Fmax *falls* **3.90%** and setup slack worsens **78.59 ps**. These percentages are increases in cost, not performance gains.

Within the speed-oriented comparison, pairwise still saves **26.09% area** relative to source, but neither design passes the 2-ns setup gate. This is a strong *negative* result for the specific timing-oriented alternative, not proof that the source cannot be repaired by other synthesis/placement choices.

## Frozen prediction adjudication and mechanism decision

- **P1 falsified:** timing-oriented ABC did not repair the source's 13.55-ps setup deficit; it worsened to 639.89 ps and introduced 22 hold and 2 max-cap violations.
- **P2 survived:** pairwise retains lower routed area than source within the speed-oriented objective.
- **P3 cautious prediction validated:** there is no unconditional pairwise timing win across mapping objectives. The speed-oriented pairwise itself fails the 2-ns setup target.
- **P4 semantic no-win remains:** same-clock, same-ports accepted grant sequences are identical. Intrinsic service-throughput ratio is 1.000x; no measured GPU IPC benefit.

**Decision:** reject `ABC_AREA=0` as a stronger *legal* source baseline at the tested corner. Retain the pairwise area-oriented implementation as the only timing-clean tested integrated variant, but do not call it globally optimal. Preserve all failures. The 4.08% isolated integrated Fmax advantage from the area-oriented run is not robust to this mapping-objective change.

## Next hard kill test
Optimize the *source* for legal setup/hold/capacitance at 2 ns using matched resource budgets, actual timing-repair choices and multiple placement seeds, and rerun pairwise with the same controls. A repaired source at comparable area/power would remove any unique timing-enabling claim. Integrate realistic SRAM/register-bank area, RF-port loads, shared bandwidth, actual tile critical paths and workload-derived activity before claiming throughput or power savings. No RTX-5090 equivalence is supported.
