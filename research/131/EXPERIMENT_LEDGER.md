# Vektor-131 evidence ledger (2026-10-12)

Type: synthetic request-round models plus **unexecuted RTL candidate**. Branch research/rf-collector-rtl-hol-131; main unchanged. Source baseline: V127–V130.

**DISCRIMINATION:** 32,768 all-ready register/mask combinations match the analytical bank-demand lower bound, with 0 residuals. **SURPRISE:** the first independent C++ replica differed from Python because it used head-of-line (HOL) blocking instead of bypassing pending operands. Both policies were retained; the initial disagreement is not claimed as validation. **EXPLOITATION:** 36,864/36,864 discovery Python/C++ comparisons and 10,240/10,240 holdout comparisons match exactly. In 8,192 unseen pending-register configurations, bypass improved 544 (6.64%), tied 7,648 and regressed 0; 2,048/2,048 no-pending controls tied. **CAPABILITY-BUILDING:** source-equation checker passed 8,192 random cases, including 6,116 with completion backpressure. The RTL and testbench have NOT run in an HDL simulator or synthesis tool.

Minimal HOL case: two valid source registers (0,2), both bank 0, register 0 pending for round 1. Bypass completes two distinct requests in 2 rounds; HOL takes 3. Same abstract bank/port budget; no equal-area or GPU-speed claim.

World model: **KNOWN** synthetic bank-demand law and exact model agreements. **BELIEVED** RTL can implement bypass and alias broadcast. **CONFLICTING** V130 registered-response multiwave cycles are not comparable with V131 request rounds. **FALSIFIED** HOL/bypass equivalence under pending operands; reset-to-zero transaction ID suffices against stale replies. **ANOMALOUS** first independent-replica policy mismatch. **UNTESTED** HDL execution, synthesis, timing, power, Wave32 RF, graphics/tensor/ray paths and RTX 5090-class gate.

Skeptic: HOL avoidance and operand collectors are prior art, and bypass logic has physical cost. Replicator: independent C++ per-bank queue model. Theorist: a work-conserving per-bank scheduler avoids preventable idle rounds for fixed finite unit read jobs; not a new architectural law.

**Single next decisive action:** run Icarus/Verilator against committed testbench, fix mismatches, synthesize with Yosys, then test two-slot collectors with write-port contention. RTX 5090-class: INCONCLUSIVE. Spend: $0.
