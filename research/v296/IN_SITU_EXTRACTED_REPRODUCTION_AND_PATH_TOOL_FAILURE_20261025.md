# V296 in-situ extracted-STA reproduction and report-command falsification (2026-10-25)

**Evidence tier: original SHA-256 verified GitHub Actions physical artifact, read-only independently checked. No critical-path endpoints recovered. No feasible integrated GPU implementation.**

## Original source and provenance

- Run: https://github.com/sushxnthd/vektor/actions/runs/40173311725
- Pairwise artifact: https://github.com/sushxnthd/vektor/actions/runs/40173311725/artifacts/12592692428
- ZIP SHA-256: `9ce2ede807ba5858efcd113b3cd4c2f9e8e5d4a6d97a7b04eb663dd354786259`
- `pairwise.high.log` SHA-256: `07edee2e676af1cb8486ffe30c4c4b6fb0a04c261ab47e9920705d69c20d3cc5`
- Independent executable audit: `python3 research/v296/in_situ_original_artifact_forensics.py --zip /path/to/v296-in-situ-path-pairwise.zip`
- Adversarial self-test: `python3 research/v296/in_situ_original_artifact_forensics.py --self-test`

The pairwise experiment **completed detailed routing with zero DRC violations**, extracted 9,159 nets and produced the original SPEF. The additional in-situ reports reproduced the original physical measurement *exactly*, before the reporting command failed:

| Pairwise integrated RF slice | Original run 40156470550 | New in-situ run 40173311725 |
|---|---:|---:|
| Extracted setup slack | -1.047895 ns | -1.047895 ns |
| Extracted hold slack | -0.036622 ns | -0.036622 ns |
| Post-route cell area | 17,857.644252 µm² | 17,857.644252 µm² |
| Capacitance violations | 3 | 3 |
| Slew violations | 0 | 0 |
| Detailed-route DRC violations | 0 | 0 |

**This is an independent repeated implementation of the failed candidate at the same settings, not a physical rescue.** It remains outside the frozen setup (+50 ps), hold (0 ps), and electrical (0 violations) requirements. The original matched serial-onehot result is also infeasible; the new serial job was still in progress at the time of this audit and is not assigned a result.

## Why path extraction failed

The path probe executed `report_checks -path_delay max -group_path_count 5 ...`. Pinned OpenROAD/OpenSTA (OpenROAD 2.0-17598) returned `STA-0563: report_checks -group_path_count is not a known keyword or flag` at `cts45_tile_in_situ.tcl:92`, **after** detailed routing, extraction, and both numerical slack reports. The path block did not complete; no setup or hold startpoint/endpoint was recorded. A job-level failure must not be confused with a failure to route, or with path evidence.

The next probe should use only pinned-compatible `report_checks -path_delay max -digits 6` and `report_checks -path_delay min -digits 6` (one worst path per group). Its Tcl changes must be read-only, symmetric, and checked before accepting any endpoint. Repeating full routing only to collect reports is expensive and does not constitute new architecture evidence.

## Correction to the prior area-frontier interpretation

The prior frontier report incorrectly stated that **the serial control could reinvest V296's 1,096.186253 µm² area saving to match V296's consumed area**. The direction was reversed. The serial control **already occupies 18,953.830505 µm²**, versus V296's **17,857.644252 µm²**. Adding area to the control cannot make its consumed area equal to the smaller candidate. At the common 30,000 µm² area ceiling, the *candidate* has 12,142.355748 µm² remaining and the *serial control* has 11,046.169495 µm² remaining. The candidate has 1,096.186253 µm² more headroom, not the control. Strict equal-consumed-area testing requires a separately optimized design pair under the same explicit resource budget; the current physical comparison is matched in constraints and functionality, not consumed area.

## Scientific decision and next kill gate

V296 and serial one-hot remain identical in admission decisions at the same clock. No throughput advantage follows from the synthetic admission law alone. V296's *relative* slack lead in two **infeasible** designs cannot be converted to an integrated GPU frequency or power improvement. V287 remains retired. Freeze the existing failure, keep the real-workload holdouts sealed, and await independent extracted setup/hold endpoints before selecting a path-specific physical repair. The new experiment must retain a strong equal-resource serial control and the original gate; reject V296 if repaired timing/area and bandwidth eliminate any tile-level gain. Kernellum PR #119 remains untouched.
