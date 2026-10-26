# V296 matched post-CTS diagnostic: independent failure forensics (2026-10-26)

## Verdict: BOTH FAIL CLOSED. No path-cone diagnostic or physical signoff.

Hosted run [40263375059](https://github.com/sushxnthd/vektor/actions/runs/40263375059) finished with **both jobs failed**, and both immutable ZIPs were recovered and independently verified. The pairwise job reached its intended post-CTS global-route checkpoint but failed at the very first timing-path report. Its pinned OpenSTA implementation rejects `report_checks -group_path_count 10` with `[ERROR STA-0563]`. The serial job reached clock-tree synthesis and began post-CTS repair but exceeded its frozen 70-minute runtime before any diagnostic reports. The candidate error is a **tool invocation failure**; the serial failure is **runtime censoring**, not a timing-path result. Neither produced the requested post-CTS critical endpoints.

| Evidence | Pairwise V296 | Optimized serial one-hot |
|---|---:|---:|
| ZIP SHA-256 | `6c1d43d33dab96fd67721479f5987ad68c12f323aeede396df31cc8b4eccacc5` | `ba1ab686ea81720bed3c4cf9cd9988ee0607e527b3670286e08be80eba234570` |
| Latest checkpoint | `cts45_postcts_global` | `cts45_clock_tree` |
| Latest checkpoint area | 16,509.556389 um² | 18,785.451417 um² |
| Latest reported setup slack | -0.270312 ns | -1.003700 ns |
| Termination | STA-0563 invalid flag | 70-minute timeout during setup repair |

**These latest checkpoints are not matched stages and must not be compared as physical PPA wins.** Both show negative setup slack; the per-stage `cap=0, slew=0` checks are not extracted electrical signoff.

## Valid common-stage comparison (diagnostic only)

Both runs did reach the same **fourth pre-CTS global-route** stage, before the serial-only fifth repair:

| Common checkpoint | Pairwise V296 | Serial one-hot |
|---|---:|---:|
| Area | 16,149.657611 um² | 18,494.979770 um² |
| Reported slack | -0.270212 ns | -0.755018 ns |

At that **non-signoff** checkpoint, candidate area is 12.680858% smaller and reported setup slack is 0.484806 ns better. Both remain setup-infeasible at the frozen 3.5 ns clock. This comparison does **not** include serial's extra fifth-round repair, so it is not a matched strongest-control final gate. It establishes only that both designs reach a common physical checkpoint and that early cone localization can be bounded without paying for a serial-only fifth repair and CTS.

## Independent reproduction and negative control

`endpoint_timeout_forensics.py` validates the exact two ZIP SHA-256 values, mandatory stage markers, reported physical numbers, the pairwise STA-0563 error, absence of any completed diagnostic, and serial's incomplete repair. Local verification passed. An altered ZIP byte was rejected by the provenance gate. Frozen machine-readable output is in `ENDPOINT_DIAGNOSTIC_FAILURE_RESULTS_20261026.json`. Download artifacts 12626562335 and 12627673135 from the hosted run, then run:

```bash
python3 research/v296/endpoint_timeout_forensics.py --self-test
python3 research/v296/endpoint_timeout_forensics.py \
  --pairwise-zip github-actions-artifact-12626562335.zip \
  --serial-zip github-actions-artifact-12627673135.zip
```

## Next falsifiable step

A **new prospectively frozen** pre-CTS fourth-stage diagnostic is separated from the failed post-CTS experiment. It stops both architectures immediately after their identical fourth-route Tcl prefix and uses only supported `report_checks` flags, with setup/hold path, DEF, and setup/hold worst slack. Its purpose is to identify actual critical cones, not demonstrate performance. The independently optimized serial-only fifth repair is retained for later final physical comparison. If either job fails or no architectural cone can be traced, no RTL repair is justified by this diagnostic.

V296 remains the sole provisional architecture mechanism. V287 is retired. No new mechanism, no measured GPU speedup, no power claim, and no RTX-5090-equivalence claim. Kernellum PR #119 and all prospective holdouts remain untouched.
