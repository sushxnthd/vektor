# V147 exact GitHub Actions evidence (2026-10-13)

Source branch: research/fp32-wave32-fma-hdl-147
Commit: c0064b86434df2e4d02212af14a25cc0fc608294

Simulator run: https://github.com/sushxnthd/vektor/actions/runs/38417325539
Status: SUCCESS; includes pytest V147 holdout cycle predictions and 2,048 randomized native glibc fmaf checks.

RTL run: https://github.com/sushxnthd/vektor/actions/runs/38417325551
Job: 115365121157
Status: SUCCESS.
Relevant exact log lines:
issue control tests passed; waiting for V146 collector HDL gate
V146 PASS: cycles=1200 completed=205 conflicts=82 bypasses=86 stalls=61 duplicate_cycles=291
./research/v146/verification/tb_wave32_operand_collector.sv:137: $finish called at 12005000 (1ps)

Collector HDL simulation: PASS (Icarus, 1,200 cycles).
Collector Yosys synthesis: NOT EXECUTED; existing RTL workflow synthesized earlier issue-control/scheduler blocks only.
V147 FMA/scoreboard RTL: NOT IMPLEMENTED; software-model only.
GPU PPA / 5090-class: INCONCLUSIVE.
