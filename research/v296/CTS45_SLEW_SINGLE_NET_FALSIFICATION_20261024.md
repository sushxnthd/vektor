# V296 post-CTS physical falsification and single-net slew localization (2026-10-24)

**Decision: CANDIDATE_CTS_PHYSICAL_GATE_FAIL.** This is a completed matched propagated-clock, detailed-route, high-RC OpenRCX experiment, not foundry signoff or a GPU-tile performance result. Preserve the sole V296 mechanism and existing draft PR; do not resurrect V287. The outcome invalidates the claim that the *current implementation* passes CTS electrical closure.

## Frozen evidence and provenance

- Workflow: https://github.com/sushxnthd/vektor/actions/runs/40093097831
- Tested commit: `5847af686dd433b7853b981d78baf9e5b1a5388f`.
- Pairwise archive: artifact `12559219137`, SHA-256 `922a974e1deabfca684c438b611615e9a94cf2fc34c691fe4f991bae1788a12c`.
- Serial one-hot archive: artifact `12560022871`, SHA-256 `5a15d85d795dfb47170eb840c505bcb33025d924b1844a2a957865853c36b49a`.
- Both ZIP digests independently checked against downloaded bytes. Local `cts45_slew_net_forensics.py --self-test` passed; both contestant logs and SPEFs were analyzed. No new RTL or repair result is claimed.
- Frozen common conditions: 3.5 ns period, 45% placement target, Nangate45, 2x extracted RC, 7,400 µm² area ceiling, propagated clocks, detailed routing, extracted SPEF, and the control's extra pre-CTS optimization round.

| Extracted metric | V296 pairwise | Serial one-hot |
|---|---:|---:|
| Final controller area (µm²) | 5,989.256 | 6,953.772 |
| Propagated-clock setup slack (ns) | +0.299279 | −0.188049 |
| Propagated-clock hold slack (ns) | +0.286195 | +0.271676 |
| Max-slew violations | **32** | 0 |
| Max-capacitance violations | 0 | 0 |
| Routing DRC violations | 0 | 0 |
| New CTS clock buffers | 3 | 3 |
| Passes frozen physical gate | **NO** | **NO** |

The candidate retains 13.8704% lower measured controller area and 487.328 ps better setup slack, but neither implementation is electrically/timing feasible. Therefore **there is no matched feasible-control Pareto victory** and no validated workload speedup. Candidate has 249.279 ps of setup slack above the 50 ps guardband; control needs 238.049 ps setup improvement to reach that guardband. Candidate has 1,410.744 µm² headroom to the *absolute* area ceiling, but only 269.138 µm² additional area at fixed control area before the *10% relative area advantage* disappears. These are algebraic budgets, not predicted repair outcomes.

## New independent root-cause localization

The post-route max-slew report lists 32 violating pins, each with a 0.250 ns limit. An independent SPEF connectivity traversal maps **all 32 pins to exactly one physical net**: `issue_wave0[0]` (SPEF `*2829`), driven by `_4758_/ZN` (an `INV_X32` cell), connected to **79 internal input pins plus one output port**. The extracted net capacitance is **0.126904 pF**. Worst slew is **0.272569 ns**, an excess of **22.569 ps**, or 9.0276% of the 250 ps limit. The 32 violating pins are not 32 independent nets. They represent 32/79 = 40.51% of internal loads, counting only internal sinks in the denominator.

The control has zero violating pins. This is an actionable **single-net fanout/transition bottleneck**, not proof that adding a buffer will fix it. In particular, one output port and the common high-fanout distribution may impose load that cannot be removed without accounting for output semantics and downstream tile loading. The extracted 0.126904 pF is the SPEF net capacitance, not a validated total downstream GPU-tile load.

Reproduction with the original archived files:

```sh
python3 research/v296/cts45_slew_net_forensics.py --self-test
python3 research/v296/cts45_slew_net_forensics.py \
  --log pairwise.high.log --spef pairwise.high.cts45.spef
python3 research/v296/cts45_slew_net_forensics.py \
  --log serial_onehot.high.log --spef serial_onehot.high.cts45.spef
```

The script checks the log's extracted slew count against individual violator rows, resolves SPEF `*NAME_MAP` aliases, maps each violating pin to a unique `*D_NET`, and fails closed on missing/ambiguous evidence. Its synthetic self-test includes malformed-count and missing-pin negative controls. The archived test returned 32 pins on one net for pairwise and zero for serial.

## Next falsifiable physical experiment

Retain the same architecture and frozen conditions. First test a **predeclared output-distribution buffering / fanout-repair policy** applied identically to both variants, with fresh CTS, routing and SPEF. Do not selectively relax the 250 ps transition limit or alter the output interface. Compare a fixed baseline policy and a fixed repair policy, not post-hoc tuning to pass a particular run. Freeze the buffer insertion and area budgets before seeing the new extracted results.

Success requires **zero** slew/capacitance/DRC violations, ≥50 ps setup margin, ≥0 ps hold margin, area ≤7,400 µm², and a completed matched control. Preserve the control's ability to repair setup timing. For a 10% area win at unchanged measured control area, candidate repair growth must be ≤269.138 µm²; for a 200 ps timing lead, differential setup deterioration cannot exceed 287.328 ps. These thresholds must be recomputed against *actual* repaired-control results. If closure or equal-resource comparison eliminates the advantage, retire V296 rather than weakening the gate.

Workload holdouts remain sealed; no claim about switching power, equal-consumed-area superiority, tile frequency, or RTX-5090 equivalence is warranted. V296 and serial one-hot have identical admission semantics, so their same-clock, same-resource issue-throughput advantage is **zero**.
