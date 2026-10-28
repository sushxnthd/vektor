# V297 five-way Nangate45 mapped strong-control falsification (2026-10-29)

**Evidence tier: HOSTED, PINNED, UNPLACED STANDARD-CELL SYNTHESIS.** GitHub Actions [run 40771315654](https://github.com/sushxnthd/vektor/actions/runs/40771315654) completed **successfully** at head `5041b5e633d7df823559c6c2bbb7d7d81f2429f8`. All five contestants used the same Nangate45 typical liberty downloaded from OpenROAD-flow-scripts revision `eda8e552974d47a12616294dddf4012d892548d3`; SHA256 `8d540a4d4cf6d09d27c87ad067857a9c0c2eeb023ab7a56e058cd3113db4e9b1`.

| Implementation | Mapped cell area (um^2) | Evidence |
|---|---:|---|
| V297 original dynamic RTL | 138.320 | Candidate implementation, superseded |
| V297 compact exact-equivalent cooldown | 126.882 | **Only provisional V297 physical candidate** |
| Optimized constant-index rotating serial | 148.694 | Stronger fair-rotation control |
| Unrestricted maximum-compatible-pair | **116.508** | **Strongest admission/area control** |
| Original dynamic-index rotating serial | 370.272 | Weak implementation, excluded from strongest-control claims |

**Matched-area result:** Unrestricted max-pair maps **8.176% smaller** than compact V297. Compact V297 maps 14.669% smaller than the optimized static rotating serial, but the unrestricted max-pair is a strictly stronger control on fixed input vectors. Replacing the weak dynamically indexed rotating controller cuts its area by 59.842% without changing its scheduling policy. This materially weakens earlier V297 hardware claims.

The corrected Python reference emitted **17,832 newline-delimited vectors**, and the clocked Icarus test passed all 17,832 comparisons across original V297, rotating serial, optimized static rotating serial, compact V297 and max-pair. Independent symbolic/seeded static-control equivalence passed 192 symbolic configurations and 120,000 concrete cases. The prospectively frozen max-pair temporal test passed in the same hosted run, including its higher-order periodic failure control. The exact `p/(1+a)` law is only valid for the declared first-order Markov model.

**Important limitation:** Mapped cell area is not placed/routed area. Yosys `ltp -noff` after ABC mapping reported path length 0, which is **not** a valid timing measurement and must not be used as evidence of a zero-delay path. There are no matched extracted-RC setup/hold, capacitance/slew, DRC, clock frequency, power or integrated GPU throughput measurements here. The static rotating control's mapped area is not a routed result.

**Stop rule:** The existing protocol requires one bounded, matched physical comparison at the frozen 3.5 ns target with equal I/O load, 2x wire RC and electrical checks. If the 116.508 um^2 max-pair control is feasible at no worse clock/physical cost, and persistent-queue fairness/throughput is no worse on unseen workloads, **retire V297**. No further claim of algorithmic novelty is justified by these results. V287/V296 remain retired.

Raw mapped synthesis logs and liberty digest are preserved in [Actions artifact 12852572221](https://github.com/sushxnthd/vektor/actions/runs/40771315654/artifacts/12852572221). Reproduction workflow: `.github/workflows/v297-bank-rescue.yml`.
