# V152 decisive negative result

V152 tested a seven-step balanced leading-one search against the unmodified V151 bounded FP32 finisher, using the same 24,220 frozen oracle vectors, interface, lane count, and generic Yosys synthesis flow.

**Functional:** 24,220/24,220 RTL differential and oracle comparisons passed; 165,540 independent Python leading-one probes passed.

**Synthesis:** V151 = 14,459 generic cells and 383 longest-path levels. V152 = 19,981 generic cells and 439 levels. This is **+38.19% generic cells and +14.62% generic depth**, not a Pareto improvement. The hypothesis that the original priority encoding dominated the critical path is falsified by this test. The alternative may introduce wide variable shifts/muxes; root cause is NOT established without critical-path tracing.

**ARCHITECTURE:** retain V151. Do not spend resources scaling V152 or claiming any GPU throughput benefit. Prioritize critical-path tracing and an actual registered arithmetic stage. No physical timing/area/power or full-GPU capability is implied.

**CI:** https://github.com/sushxnthd/vektor/actions/runs/38450952077 (PASS; success means correctness and evidence capture, not performance). Raw Yosys logs and differential logs: https://github.com/sushxnthd/vektor/actions/runs/38450952077/artifacts/11840199049.

**SCIENCE:** established leading-one circuits are prior art. No publishable novelty. Preserve this negative result to prevent rediscovery.
