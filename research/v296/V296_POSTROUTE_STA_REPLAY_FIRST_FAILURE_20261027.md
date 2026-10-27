# V296 extracted-SPEF replay: independently preserved first-run failure (2026-10-27)

Source: [GitHub Actions #40450922762](https://github.com/sushxnthd/vektor/actions/runs/40450922762). Both matrix jobs failed **after** reading routed DEF and extracted SPEF and printing the numerical worst slacks. No named critical-path attribution is possible from this first attempt.

| Evidence | V296 pairwise | Optimized serial onehot |
|---|---:|---:|
| Original routed artifact ID | 12703514184 | 12703682763 |
| Original artifact ZIP SHA-256 | `c0d90c6652deba498c46e6b01e9d3e1ce0317505caf833eea51323b54e6f49a7` | `928adb671004dea251dc9c1c558f87a34fc3d3ff233e66d41ddd311d3d305ea4` |
| Failed replay artifact ID | 12710432390 | 12710871417 |
| Failed replay ZIP SHA-256 (independently checked) | `94ed3137a32d5a4362cc9fc6c1aca86c4a7372b3154d62bd5932c68b85a325ef` | `9033d62112be8f57c4258828fa87af32353afd799a9dd662a47ac37c9f5692c2` |
| Replayed setup slack | -0.220829 ns | -0.711405 ns |
| Replayed hold slack | -0.010023 ns | -0.013032 ns |
| Difference from original | 0.000000 ns both | 0.000000 ns both |
| Named path report | **FAIL STA-0563** | **FAIL STA-0563** |

Both logs contain `[ERROR STA-0563] report_checks -group_path_count is not a known keyword or flag.` at `replay.tcl:38`. This is a **command compatibility failure**, not evidence of an inaccurate reconstructed timing network. The fail-closed checker correctly returns `INCOMPLETE_NO_EXTRACTED_PATH_CLAIM` because no named path and final marker exist.

The narrow amended replay requests the default single worst path with supported `report_checks -path_delay max|min -fields {slew capacitance fanout} -digits 6`. No timing threshold, source artifact, electrical constraint, clock or RC scaling changed. The decoded density-0.35 implementation remains rejected regardless of path reconstruction outcome. This evidence tier is not a feasible GPU performance result.
