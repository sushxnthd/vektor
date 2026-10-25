# V296 integrated RF-slice: candidate extracted physical gate FAILED (2026-10-25)

**Evidence tier:** original paired physical run [40156470550](https://github.com/sushxnthd/vektor/actions/runs/40156470550), independently inspected candidate artifact [12585654946](https://github.com/sushxnthd/vektor/actions/runs/40156470550/artifacts/12585654946), post-CTS propagated-clock detailed route, 2x OpenRCX extracted RC. **Not silicon signoff.** This report freezes the **candidate-only** observation while the serial-onehot control job remains pending. No paired area/timing victory can be inferred.

## Preregistered gate versus observed candidate

Frozen protocol: [TILE_SLICE_PHYSICAL_PREREG_20261025.md](TILE_SLICE_PHYSICAL_PREREG_20261025.md). Same 32-wave scheduler, 4 issue slots, 16 RF banks, 2 read ports per bank, one global write port, and 8-bit execution slice. The two RTL implementations passed 2,048-cycle randomized/adversarial equivalence with 0 grant/execute mismatches. Same-clock admission gain = **zero**.

| Candidate extracted metric | Frozen acceptance gate | Observed |
| --- | ---: | ---: |
| Cell area | <=30,000 um² | 17,857.644252 um² (pass) |
| Setup slack | >=+0.050 ns | **-1.047895 ns (FAIL)** |
| Hold slack | >=0 ns | **-0.036622 ns (FAIL)** |
| Max-slew violations | 0 | 0 (pass) |
| Max-capacitance violations | 0 | **3 (FAIL)** |
| Detailed-routing DRC | 0 | 0 (pass) |

The setup gate misses by **1.097895 ns** and the hold gate by **0.036622 ns**. Capacitance violators in the original extracted log: _12573_/ZN 13.085626 fF versus 11.482200 fF; _10310_/ZN 12.548141 versus 11.482200; _09621_/ZN 26.040531 versus 25.634800. The tool job completed and uploaded evidence, but **the candidate is physically infeasible under the frozen integrated-slice acceptance criteria**. A successful GitHub job or completed detailed route is not equivalent to electrical/timing closure.

## Independent path attribution and limitations

The mapped netlist independently maps the first *pre-CTS* register-to-register report startpoint _15188_ to \\candidate.issue.scheduler.rr1 [1] and endpoint _15156_ to executed_data[7]. This identifies an observed scheduler-to-execution register path in the earlier timing stage, not the final extracted worst path. The final extracted log reports worst setup slack but does not supply a full post-CTS critical-path trace. Do not claim the final critical path is arbitration-only or attribute the -1.047895 ns deficit to a particular sub-block without a post-CTS path report.

Independent forensic checker: [integrated_slice_failure_forensics.py](integrated_slice_failure_forensics.py). Original artifact SHA256: `06bfdd796801728553fa6c42e853957fb681e52731c73641a9aed403f2905544`. It cross-checks raw log versus independent audit, fails closed on missing markers or inconsistent metrics, and labels the earlier path correctly. Reproduction: download the original artifact, unzip, run `python3 research/v296/integrated_slice_failure_forensics.py --self-test`, then `python3 research/v296/integrated_slice_failure_forensics.py --root <unzipped-folder>`.

## Scientific decision

**The integrated candidate physical feasibility hypothesis is falsified.** Even a physically feasible serial control cannot rescue this candidate's absolute negative setup/hold and cap violations. The preregistered >=1% area-saving and >=50 ps slack-lead *paired* Pareto verdict still requires the serial control's original artifact and the existing independent aggregate checker; do not fill in missing control measurements. The prior controller-only +325 ps setup-slack observation does **not** establish an integrated GPU frequency gain. The mapped integrated area saving was only 0.731714%, below the exploratory 1% target at the synthesis stage.

V296 remains the sole mechanism under falsification, not a surviving physically validated GPU-tile mechanism. Do not quietly change clock, floorplan, repairs or thresholds after this failure. Preserve all negative evidence and sealed holdouts. No full-tile Fmax, real workload throughput, power or RTX-5090-equivalence claim is justified. V287 remains retired. Kernellum PR #119 remains independent.
