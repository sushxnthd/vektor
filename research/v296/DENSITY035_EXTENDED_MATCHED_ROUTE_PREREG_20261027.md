# V296 density-0.35 matched extended-route checkpoint: prospective protocol (2026-10-27)

## Reason for experiment

The previously preregistered symmetric density-0.35 experiment (Actions run 40411106938) established 3,632 V296 candidate detailed-route violations at **completed iteration 3**, but its independently optimized fifth-stage serial control was censored **before entering detailed route** after 75 minutes. This is an *informatively missing control*, not evidence of a V296 win. The original density-0.45 physical baseline (run 40359299905) and both 75-minute diagnostic artifact hashes remain unchanged in `DENSITY035_FROZEN_ROUTE_FORENSICS_20261027.json`.

## Frozen intervention and resource policy

- **One mechanism only:** V296 pairwise bank-conflict admission, with the existing symmetric one-hot bank decoder. V287 stays retired.
- **Branch and PR:** `research/v296-pairwise-bank-conflict`, draft PR #13. No new architecture branch.
- **Physical inputs:** unchanged RTL, 3.5 ns clock, 2.0x resistance/coupling/ground-capacitance scaling, Nangate45 library, fifth-stage serial timing repair, placement density 0.35 for both, identical generated diagnostic Tcl, floorplan and routing commands.
- **Time allocation:** a fresh matched run with **210 minutes per contestant**, plus approximately 20 minutes for dependency installation/artifact upload. Both contestants receive the same time cap, even if one reaches detailed routing earlier. Runner exits 124/137 must be preserved as censoring, not converted into success.
- **Original density-0.45 controls** are fixed; no thresholds may be recalibrated after seeing this new run. All workload holdouts remain sealed.
- **Cost discipline:** one matched extension only, no automatic retrial or parameter sweep. Any failed or incomplete physical execution must be recorded before another experiment.

## Prospective, unchanged checkpoint and rejection rules

At the **completed** detailed-route iteration 3 for both contestants:

1. Candidate V296 DRC <= **8,414**, i.e. at least 30% below the original 12,020.
2. The ratio `(DRC_V296_035/DRC_serial_035)/(12020/5281)` <= **0.75**.
3. Any missing iteration-3 measurement yields **INCOMPLETE_CONTROL_OR_CANDIDATE_CENSORED**; it must never be imputed as zero. Both requirements are conjunctive.
4. If candidate 3,632 repeats exactly, serial iteration-3 DRC must be >= **2,128** to satisfy requirement 2. This threshold is a *partial-identification bound*, not a forecast.

Passing both is only a **routing-diagnostic result**. To survive as physically credible, the decoded candidate and an equal-resource optimized serial baseline must independently finish detailed routing with DRC=0, extracted setup slack >= +0.050 ns, hold >=0, zero capacitance and slew violations, cell area <=30,000 um^2, and comparable bandwidth/port constraints. Workload-level gains must use actual feasible clocks. No GPU speedup is claimed from DRC counts, estimated setup, or unfinished routing.

## Kill criteria

- If the extended candidate fails to reach DRC=0 or fails extracted electrical/timing requirements, **reject density-0.35 as a sufficient decoded-V296 physical rescue**. Do not endlessly extend time budgets.
- If both complete iteration 3 but either checkpoint gate fails, reject the **relative routing-congestion hypothesis** even if candidate-only DRC decreases.
- If serial remains censored at 210 minutes, report the comparative hypothesis as unidentifiable and reject this resource-bounded matched experiment as a basis for architectural advantage. No selective deletion of fifth-stage serial optimization.
- A physically infeasible or bandwidth-erased speedup kills the decoded implementation, regardless of analytical bank-admission predictions. Preserve negative results.

## Evidence discipline

Commit the prospective protocol **before** launching the workflow. Capture original artifacts and hashes, full completed DRT trajectories, explicit tool exit codes, both contestant provenance manifests, and the fail-closed independent audit. Use no force-push, merge, or unrelated workstream writes. Kernellum PR #119 is not part of this experiment.
