# Rounding-robust clock/occupancy no-win sensitivity (2026-11-19)

Evidence tier: exact rational **conditional arithmetic** applied to six-decimal **historical oracle service ratios**, not new physical design, finite-buffer throughput, or GPU IPC. This exploratory sensitivity is not a prospective confirmatory workload test.

Script: `research/v317/rtl/rounded_service_threshold_sensitivity_20261119.py` (self-test and table). Inputs are published six-place rounded oracle/compact-greedy ratios from the existing research; every input is enveloped by +/- 0.0000005. With target T=1.02, service ratio s, clock ratio f, occupancy ratio o, and externally imposed bandwidth ceiling b, the assumed proportional-service upper bound is G<=min(b,s*f*o). This is **not** a universal upper bound for a different queueing discipline or changed workload distribution. A necessary condition for a material win is b>=1.02 and f*o>=1.02/s. For rounded s, the necessary product threshold lies in [T/(s+eps),T/(s-eps)]. Crossing the upper endpoint only avoids this one falsifier, never proves a win.

| Historical regime | Service ceiling | Necessary f*o interval | Necessary f at o=0.95 interval |
|---|---:|---:|---:|
| uniform16 | 1.001025 | 1.01895506–1.01895608 | 1.07258428–1.07258535 |
| uniform4 | 1.046155 | 0.97499846–0.97499939 | 1.02631417–1.02631515 |
| hot50 | 1.072037 | 0.95145925–0.95146014 | 1.00153606–1.00153699 |
| hot65 | 1.106717 | 0.92164441–0.92164525 | 0.97015201–0.97015289 |
| hot75 | 1.119826 | 0.91085539–0.91085620 | 0.95879514–0.95879600 |
| hot875 | 1.080401 | 0.94409347–0.94409434 | 0.99378260–0.99378352 |

**New conditional falsification:** with a 5% occupancy penalty and no clock improvement, the uniform-four-bank regime cannot reach the 2% gate even if a zero-cost oracle captures its entire historical instantaneous-service ceiling. The 50%-hot case is also below the gate at f=1, o=0.95. Uniform-16 needs >7.25% clock uplift at o=0.95. At b<1.02, **every** regime fails regardless of its theoretical service ceiling.

The oracle is unfair and has zero modeled area/timing cost, so these bounds are optimistic. The stronger compact-greedy implementation still beats V317 pairwise on historical routed whole-proxy area (21,314.6 versus 21,324.7 um^2), and both routes violate electrical constraints. No positive physical or integrated-tile claim survives. **Do not revive V287, relax the frozen >=2% gate, infer GPU IPC, or claim legal timing/DRC, SRAM integration, calibrated power, or RTX-5090 equivalence.**

Next decisive work: freeze a finite-buffer prospective workload test (including uniform16 no-win and hot65 conditional-win) and implement a physically legal, equal-resource competitor before promoting any positive law. Verify workflow execution and provenance separately.
