# V296 decoded post-CTS: strongest serial-control physical failure (2026-10-27)

**Partial paired result, not a matched architectural win.** The frozen decoded post-CTS extracted-RC experiment is GitHub Actions [run 40359299905](https://github.com/sushxnthd/vektor/actions/runs/40359299905). Its `paired-postcts-extracted (serial_onehot)` job 121706697816 completed successfully as a **workflow**, but the independent contestant physical audit returned `physically_feasible: false`.

## Original hosted physical record
- Original completed artifact: `v296-decoded-postcts-serial_onehot`, artifact ID **12681568761**, ZIP digest **sha256:36c9ce00caadf2416082510a6b9a84cbbd5c8a4b26dce646b7ecb19ed7682713** (GitHub Actions upload log).
- Evidence tier: post-CTS propagated-clock, detailed-route, extracted OpenRCX, **not signoff**.
- Provenance checker: **PASS**. Reported physical experiment complete: **true**.
- Pre-CTS area **17,405.710651 um²**; post-CTS area **17,482.850723 um²**; final area **17,917.228590 um²**.
- Extracted setup slack **-1.328847 ns** against frozen **+0.050 ns** requirement. Required setup repair to reach guard: **1.378847 ns**.
- Extracted hold slack **-0.013450 ns** against nonnegative requirement; capacitance violations **4**; slew violations **0**.
- Clock-tree increment **77.140072 um²**, 43 new clock buffers.
- Reported issue_wave0[0] net `*6645`: **0.0331144 pF**, 17 pins, 15 loads. This is forensic context, not proof of a unique critical cause.
- No independent DRC count is asserted in this partial note. Do not interpret absent DRC reporting as zero violations.

## Decision
The strongest serial contestant **fails** the frozen 3.5 ns electrical/timing feasibility gate. This is a **negative physical result** even though the job completed and uploaded evidence. The V296 paired candidate job was still running when this note was committed. Therefore neither a matched feasible Pareto advantage nor a GPU speedup can be claimed; the pair's full physical verdict remains pending. Do not change clock, RC, floorplan, CTS, repair policy or seed to obtain a favorable result. Once candidate completes, apply the original fail-closed independent paired checker to both original artifacts. V296 remains sole provisional mechanism; V287 retired.
