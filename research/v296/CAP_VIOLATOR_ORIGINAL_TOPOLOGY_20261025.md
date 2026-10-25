# V296 integrated RF-slice: original extracted cap-violator topology (2026-10-25)

**Result:** Independently traced all six original post-route maximum-capacitance violations through the exact original archived Nangate45 physical logs, routed DEF, mapped Verilog and SPEF. Both original ZIP SHA256 hashes match the preregistered provenance. This is a **physical/electrical falsification diagnostic**, not a new architecture victory or a recovered setup critical path.

| Variant | Driver/cell | Pin cap / limit (fF) | Excess (fF) | SPEF net cap (fF) | Sinks | Max driver-to-sink Manhattan distance (µm) |
|---|---|---:|---:|---:|---:|---:|
| V296 | `_12573_/ZN` OAI33_X1 | 13.085626 / 11.482200 | 1.603426 | 12.1392 | 1 | 37.97 |
| V296 | `_10310_/ZN` OAI33_X1 | 12.548141 / 11.482200 | 1.065941 | 10.7689 | 1 | 34.93 |
| V296 | `_09621_/ZN` AOI222_X2 | 26.040531 / 25.634800 | 0.405730 | 22.6387 | 1 | 76.25 |
| Serial one-hot | `_08763_/ZN` OAI33_X1 | 13.615290 / 11.482200 | 2.133090 | 10.9476 | 2 | 30.82 |
| Serial one-hot | `_08736_/ZN` OAI33_X1 | 13.440553 / 11.482200 | 1.958353 | 8.65746 | 2 | 25.00 |
| Serial one-hot | `_11518_/ZN` OAI33_X1 | 11.817500 / 11.482200 | 0.335301 | 8.68774 | 1 | 26.72 |

**New falsification:** The six cap violations are **not explained by large logical fanout**: every offending net has only one or two sink pins. Three candidate nets terminate at a MUX2 or an inserted BUF_X2/BUF_X4; the longest candidate source-to-sink placement Manhattan separation is 76.25 µm. Serial's two-sink nets include repair-inserted buffers. This supports investigating **routed wire capacitance and weak complex-gate drivers**, rather than assuming fanout reduction alone will repair the design. Manhattan distance is a placement lower bound, not routed wire length; SPEF net cap is not the same quantity as STA's pin total, which also includes sink capacitance.

**Immutable provenance:** Original run 40156470550; V296 ZIP SHA256 `06bfdd796801728553fa6c42e853957fb681e52731c73641a9aed403f2905544`; serial ZIP SHA256 `5456c370dc860daa67aa61c7a8dc9937291f2b5d89e4e8e51c4ebedf14c6fd1d`. Original worst setup/hold (ns): V296 −1.047895/−0.036622; serial −1.859922/−0.019796. Both have three cap violations and zero slew violations. The independent script `research/v296/cap_topology_audit.py` rejects altered ZIP hashes, mismatched original slacks, missing nets, inconsistent cap arithmetic and absent physical sinks.

**Decision:** Original integrated physical gate remains **FALSIFIED for both contestants**. No feasible Fmax, GPU speedup or power claim. A new equal-resource physical repair must be prospectively frozen and run symmetrically; do not reopen sealed workload holdouts. Extracted worst setup/hold path endpoints remain unknown until independent STA reconstruction agrees with original measured slacks.
