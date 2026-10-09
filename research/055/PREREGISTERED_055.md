# Vektor-055 frozen predictions (before RTL CI)

**Class:** DISCRIMINATION + CAPABILITY-BUILDING. The software grid and 64-seed exploratory holdout were run before this document was committed; do not call them independently preregistered. The following RTL/synthesis predictions are frozen before the 055 CI run.

1. A per-operand validity mask will allow 0/1/2/3-source instructions, including holes. Invalid earlier operands cannot suppress a valid dedup root, and invalid operands cannot block completion or receive fanout.
2. All 40 deterministic 1,500-cycle RTL differential vectors (60,000 cycles) will match the Python reference, with zero tag/data mismatches. **Any RTL mismatch falsifies equivalence.**
3. Zero-alias DEDUP=0 and DEDUP=1 controls will have identical request and completion counts. **Any difference falsifies the control.**
4. Generic Yosys synthesis will show nonzero dedup logic overhead; exact cell count is not predicted. This is not physical area/timing/power.
5. A pinned public PTX corpus check will reproduce BPF counts (272 eligible instructions, 564 register-source uses, 10 repeats, 20 three-source ops, 0 three-source repeats) and compiler-produced vector-add counts (6, 13, 0, 1, 0). Any mismatch invalidates the PTX-mix proxy pending investigation.

**Model limitations:** two slots, one request port, no actual RF banks, physical register allocation, scoreboard, dynamic workload trace, graphics/ray path or technology-mapped PPA. PTX source-identity counts are static virtual-register observations, not hardware measurements.

**Next decisive experiment:** CI RTL differential, equal-budget generic synthesis, then a banked 4/8/16-slot collector with realistic dynamic operand traces.
