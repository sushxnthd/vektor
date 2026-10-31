# V317 frozen parameter-width synthesis sensitivity (2026-11-01)

This protocol is committed **before** opening the new 8x16 and 32x32 Yosys outcomes. It extends the already validated forwarding-admission RTL, not a new mechanism or branch.

## Fixed sweep and predictions

Use the exact existing SystemVerilog design and identical generic Yosys `synth; stat; ltp -noff; write_json` flow. Three configurations are fixed:

| Lanes | Bits per lane | Warp-ID bits | Register-ID bits | Bank-ID bits |
|---:|---:|---:|---:|---:|
| 4 | 8 | 2 | 4 | 2 |
| 8 | 16 | 3 | 6 | 3 |
| 32 | 32 | 5 | 8 | 4 |

Predictions: larger lane/data widths must require **more generic combinational cells** than the 4x8 control, because a valid forward must drive a wider masked data path; exact counts, logic levels and net fanout are held out. A strong same-information baseline can use identical forwarding, so there is **no incremental modeled transaction advantage** at any width. The lane-granular clean-mask positive functional regime and cross-warp/dirty-lane no-win regime remain as in the earlier frozen protocol.

Record generic cell count, longest topological path (gate levels), maximum generic net fanout, and forward-grant net fanout from Yosys netlists. Do not interpret fanout as physical capacitance, gate levels as nanoseconds, or generic cell counts as standard-cell area. The buffered data source, dirty-mask generation, broadcast/invalidation wiring, RF cache, compiler behavior, tile occupancy and real workload traffic are absent.

## Kill rule

If wide configuration fails synthesis or reveals unbounded fanout/logic overhead, do not claim physical feasibility. If the baseline is allowed the same resources, any putative incremental architectural gain remains zero regardless of generic cell scaling. No RTX 5090 equivalence.
