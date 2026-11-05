# V309 independent profiler-counter audit protocol (2026-10-30)

Status: **EXPLORATORY EXTERNAL EVIDENCE**, not a hardware candidate or matched GPU validation. Preserve single V309 branch and draft PR #26. No V287/V296 revival.

## Source and integrity
Use the Accel-Sim project's publicly published `util/accelwattch/accelwattch_hw_profiler/hw_perf.csv` at immutable upstream commit `7ba54ded60c4ba0083410c37d22d719166acd6dc`, Git blob SHA-1 `aa88bb2566ff3b3e012442cd20bc753127732cac`. The file is described by the upstream project as sample GV100 profiler counters for AccelWattch; its precise profiler collection conditions and counter units are not independently authenticated here. Fetch only this small CSV and reject any hash mismatch. Do not equate counts across different counter domains or assume byte units.

## Questions (exploratory; source was inspected before this protocol)
1. Can a universal multiplicative L1 read-miss-to-DRAM-read estimator exist for every positive-DRAM kernel in the file? Any row with L1_RM=0 and DRAM_Rd>0 falsifies that restricted zero-intercept form.
2. How widely does DRAM_Rd/L1_RM vary among rows where L1_RM>0? Report min/max and the exact kernel identities; do not fit a speedup model.
3. How does the stronger L2_RM proxy compare, including rows where L2_RM=0 and DRAM_Rd>0? Do not equate L2 misses to DRAM transactions even if most rows are close.
4. Are the suite names, kernel identifiers and inputs matched to the V309 Rodinia 2.0-ft SASS trace archive? Require explicit version/configuration/provenance equality; overlapping names alone do not qualify.
5. Independent parser and numeric checker must reject nonfinite, negative, malformed or duplicate benchmark+kernel rows; report raw count and all excluded cases.

## Stop/kill criteria
Any zero-miss positive-DRAM row kills the zero-intercept L1-only counter proxy on this dataset. A similar L2 zero row kills its zero-intercept counterpart. If provenance is unmatched, forbid joint per-kernel regression, claims of observed sector-to-DRAM conversion, measured throughput, hardware opportunity, and physicality promotion. Never interpret the ratio as a cache hit rate or as a measured byte conversion.

## Reproducibility
Python standard library only; a small source-pinned download, independent arithmetic oracle, exact summary JSON, hosted CI. Keep prior V309 source-conditional trace interval and all negative results unchanged. No unseen-workload claims: this is an exploratory counter audit of already inspected public data.
