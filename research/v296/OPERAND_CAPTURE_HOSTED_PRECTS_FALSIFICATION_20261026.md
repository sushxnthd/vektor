# V296 operand-capture retiming: hosted mapped and pre-CTS falsification (2026-10-26)

**Decision: no physical performance claim.** The prospectively registered symmetric operand-capture experiment completed on GitHub Actions run [40288329940](https://github.com/sushxnthd/vektor/actions/runs/40288329940). Both RTL/oracle, all four mapped syntheses, and both bounded pre-CTS physical jobs completed successfully as *experiments*. Neither implementation passes the frozen 3.5 ns setup gate, and neither meets the additional +50 ps setup guard. V296 remains the sole provisional mechanism under falsification; V287 is retired.

## Frozen evidence and independent replication

Use the exact original artifact ZIPs, **not copied console summaries**:

| Artifact | ID | ZIP SHA-256 |
| --- | ---: | --- |
| Four-way Nangate45 mapped synthesis | 12635208974 | `0de959a98a7185bde3bbcebbb7412c0cfb56900c4e18cdef497ff3468b181a74` |
| Pairwise operand-capture pre-CTS | 12635812416 | `a3d96cfd3967c535531e7ef9ebb0cb8d0bfe5dfeadf6005b424e34646a6c9c6e` |
| Serial operand-capture pre-CTS | 12636698060 | `60e63f1d7f330bd8d3786a511830c80c7e55f5c069a69252cdafd09432b52a15` |

Run `python3 research/v296/operand_capture_hosted_audit.py mapped.zip pairwise.zip serial.zip`. The independent checker reads all three ZIPs, rejects mismatched digests, checks four mapped areas, checks matched experiment manifests, extracts setup/hold/electrical metrics, and maps the critical-path flop endpoints to the actual mapped netlists. Its frozen output is [OPERAND_CAPTURE_HOSTED_AUDIT_20261026.json](OPERAND_CAPTURE_HOSTED_AUDIT_20261026.json). A local adversarial test altered one byte in the mapped ZIP; the checker correctly failed closed with a digest mismatch. The untouched original ZIPs passed.

## Same-library synthesis: retiming costs real area

| Implementation | Mapped area (µm²) | Relative to its unretimed version |
| --- | ---: | ---: |
| Unretimed pairwise | 8,880.676 | reference |
| Unretimed serial | 9,589.300 | reference |
| Retimed pairwise | 9,374.106 | **+5.556%** |
| Retimed serial | 10,217.858 | **+6.555%** |

At this mapped-only tier, retimed V296 is **8.258% smaller** than retimed serial. This is a gate-area observation, not post-route area, consumed-area equality, or dynamic power. The retiming adds 88 bits of nominal pipeline state before synthesis optimization; its latency and switching costs cannot be ignored.

## Matched fourth-stage pre-CTS global route

| Frozen measurement | Retimed V296 | Retimed serial |
| --- | ---: | ---: |
| Intermediate area (µm²) | 15,818.221 | 16,932.496 |
| Setup slack at 3.5 ns (ns) | **−0.025959** | −0.406435 |
| Worst reported hold slack (ns) | +0.112872 | +0.112877 |
| Reported slew violations | 0 | 0 |
| Reported capacitance violations | 0 | 0 |
| Missing margin to +50 ps setup guard | **75.959 ps** | 456.435 ps |

V296 has **6.581% lower intermediate area** and **380.476 ps less-negative setup slack**. These are *pre-CTS global-route estimated-parasitic* measurements with ideal clock assumptions. They are **not** post-CTS, detailed-route, extracted-RC, DRC, or electrical signoff. Zero intermediate cap/slew violations is not proof of final electrical closure. The serial control's independently optimized fifth-stage repair is not included in this experiment, so this is not the ultimate strongest-control comparison.

The prior unretimed fourth-stage experiments reported −0.270212 ns for V296 and −0.755018 ns for serial. The new retimed observations are respectively 244.253 ps and 348.583 ps less negative. These are **cross-run comparisons**, not a controlled within-run estimate of retiming's causal benefit; do not use them to claim frequency improvement.

## Critical-path attribution and mechanism

The candidate's critical path runs from `candidate.issue.scheduler.rr0[1]` (mapped flop `_12667_`) to `staged_operand_data[6][5]` (mapped flop `_12646_`). The serial control runs from `strongest_serial.issue.scheduler.rr1[2]` (`_13413_`) to `staged_operand_data[2][6]` (`_13363_`). Both paths therefore still cross scheduler/control and register-file operand-selection logic. The inserted boundary removes the downstream execution arithmetic from this stage, but **does not remove the scheduler-to-operand-selection bottleneck**. The +50 ps setup guard remains violated.

The one-cycle execution delay was checked against the independent register-file oracle in 4,096 hosted checks over 2,048 cycles, including 6,589 admitted operations. That is useful functional evidence, **not** a proof of arbitrary multi-cycle dependency handling, backpressure, memory ordering, or GPU workload-level throughput. A nominal initiation interval of one does not imply unchanged throughput on dependent workloads.

## Falsification and next physical decision

The preregistered strict closure gate fails for **both** contenders. V296's relative area/timing lead is not a viable architectural speedup until both clocks close at matched resources and the strongest serial repair is included. Same-clock issue admissions remain identical; there is no intrinsic same-clock admission-throughput win. A hypothetical area-reinvestment advantage requires additional physically feasible slices and sufficient bandwidth, and the retimed extra latency can negate it for dependency-heavy workloads.

Next, isolate the scheduler-to-`staged_operand_data` fanout, RF read selection, and wire/load contribution using the preserved mapped netlists and pre-CTS critical cones. Preregister a *symmetric* local control/operand-select repair and test its RTL equivalence and physical impact. If the repaired V296 still fails matched routed setup/hold/electrical closure, or a fully optimized equal-resource serial implementation matches it, reject the GPU performance claim rather than relax the original gate. Preserve negative artifacts, real holdouts, and the one-mechanism rule.

**Evidence ceiling:** mapped synthesis + pre-CTS global-route estimated timing. No measured Fmax, power, final routability, equal-resource throughput superiority, or RTX-5090 equivalence. Kernellum PR #119 is not changed by this study.
