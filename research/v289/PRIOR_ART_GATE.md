# V289 prior-art and scope gate (2026-10-23)

The mechanism is **not novel as a general criticality-aware GPU scheduler**. Relevant prior work:

- Lee & Wu, "CAWS: Criticality-aware warp scheduling for GPGPU workloads," PACT 2014, DOI 10.1145/2628071.2628107. Studies GPU warp criticality and criticality-aware warp scheduling.
- "CAWA: Coordinated warp scheduling and cache prioritization for critical warp acceleration of GPGPU workloads," ISCA 2015, DOI 10.1145/2749469.2750418. Uses a criticality predictor and prioritizes critical warps in scheduling.
- "Triple-A: Early Operand Collector Allocation for Maximizing GPU Register Bank Utilization," IEEE Embedded Systems Letters 2024, DOI 10.1109/LES.2023.3307622. Explicit operand collector scheduling and RF forwarding.
- "BOW: Breathing Operand Windows to Exploit Bypassing in GPUs," MICRO 2020, DOI 10.1109/MICRO50266.2020.00084.

**Narrow possible contribution:** physical area/timing/energy and DAG-makespan characterization of one-bit criticality at *register-bank request admission* in Vektor's exact collector interface, if it survives equal-budget urgency-aware scheduling and prior art. No new-principle claim.

**Structural bound already checked:** both age-first and V289 issue exactly one request per occupied bank. Across 4096 independent Python configurations, zero grant-cardinality mismatches, 584 selection differences. Thus no improvement in raw bank grants per cycle is possible; any performance gain must be proven in critical-path DAG makespan, not average grants. Frozen win/no-win workload regimes remain unopened.

**Next gate:** build a DAG-driven workload model with identical two-bank/one-port/four-request resources and urgency-bit matched controls; synthesize/STA with realistic loads. Kill if equal-budget criticality-aware control matches or area/frequency cost erases any DAG win. No integrated tile change.
