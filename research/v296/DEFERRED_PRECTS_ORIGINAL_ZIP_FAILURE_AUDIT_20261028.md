# V296 deferred-write matched pre-CTS: original-artifact instrumentation failure and conditional area boundary (2026-10-28)

## Scientific decision

**The frozen matched pre-CTS run is INCOMPLETE, not passed.** All four contestant jobs in [Actions #40629351716](https://github.com/sushxnthd/vektor/actions/runs/40629351716) ended with `EXIT_CODE=4`. The OpenROAD script reached its final estimated-RC global-route timing/area/electrical measurements but then hit `[ERROR STA-0563] report_checks -group_path_count is not a known keyword or flag.` No `V296_DEFERRED_PRECTS_DONE` marker was emitted. The original fail-closed aggregate must continue to reject this run. A GitHub Actions job labeled `success` is only an evidence-preservation success, **not physical validation**.

An independent original-ZIP audit, pinned to the four uploaded ZIP SHA-256 digests, recovered the intermediate measurements below. The ZIPs retain the 3.5 ns clock, 2x estimated RC, density 0.45, 16 banks, 2 read ports/bank, one global write, and strongest fifth-stage optimized serial control. No holdout was opened.

| Same-depth design | Area (um2) | Setup slack (ns) | Cap | Slew | Runner |
|---|---:|---:|---:|---:|---|
| D4 V296 pairwise | 18794.230172 | +0.381283 | 0 | 0 | EXIT 4 |
| D4 optimized serial | 20763.694764 | +0.150760 | 0 | 0 | EXIT 4 |
| D8 V296 pairwise | 25645.858770 | +0.214891 | 0 | 0 | EXIT 4 |
| D8 optimized serial | 26891.802563 | +0.110820 | 0 | 0 | EXIT 4 |

**Intermediate estimated-RC comparison only:** V296's area advantage is 1969.464591 um2 (9.4851%) at D4 and 1245.943793 um2 (4.6332%) at D8. Its setup-slack advantage is +230.523 ps at D4 and +104.071 ps at D8. All four measured intermediate points exceed the +50 ps setup guard and show zero reported cap/slew violations, but the **completed-run gate is not met** and no CTS/extracted-RC/hold feasibility is established. These figures must not be cited as final physical wins.

## Predictive integer-packing boundary (conditional on these intermediate areas)

With a 30,000 um2 tile-area ceiling, both designs fit **one** complete slice at either depth. Therefore the intermediate area advantage does **not** increase tile-slice count at the frozen budget.

At D4, two V296 slices first fit at 37588.460344 um2; two serial slices require 41527.389527 um2. At D8, the corresponding thresholds are 51291.717540 and 53783.605125 um2. These conditional windows are **not** prospective GPU wins: post-CTS area, routing feasibility, clock, bandwidth, occupancy, deferred extra-cycle latency and power remain unvalidated. The already frozen finite-occupancy frequency break-even law remains binding. A shared bandwidth cap can erase extra-slice throughput entirely.

## Falsification, repair and audit

The failure is an instrumentation/API incompatibility, **not evidence that the candidate failed its estimated-RC timing guard**. The exact original ZIP SHA-256 values, source run, intermediate measurements, explicit nonzero exit and incomplete evidence tier are in [machine-readable results](DEFERRED_PRECTS_ORIGINAL_ZIP_FAILURE_AUDIT_20261028.json). [Independent ZIP checker](deferred_prects_original_zip_audit.py) rejects corrupted artifacts, missing stage markers, altered controls and any attempt to treat the failed runner as completed.

Repair **only** the unsupported `-group_path_count 3` report option in the generated diagnostics. Do not alter physical RTL, constraints, placement, serial fifth-stage control or the preregistered +50 ps gate. The repaired workflow must rerun all four contestants, emit `V296_DEFERRED_PRECTS_DONE`, pass the existing fail-closed independent aggregate, and preserve original failure artifacts. Only then consider a bounded matched extracted-RC route experiment. No RTX-5090-equivalence, GPU throughput or power claim.

V296 remains the sole provisional architecture mechanism; V287 remains retired. Kernellum PR #119 and prospective holdouts remain untouched.
