# V149 validated evidence (2026-10-13)

Branch: research/fp32-wave32-close-round-149
Verified commit: d30bc46140300126a94cd0920b51c98d47758799
GitHub Actions: https://github.com/sushxnthd/vektor/actions/runs/38430988476
Outcome: SUCCESS on free Ubuntu runner, Icarus 12.0 and Yosys 0.33.

- Independent exact-dyadic RNE oracle vs glibc fmaf: 3072/3072 real-FP32 CLOSE result bits matched (seed 149, including subnormal underflow, signed zero, ties and randomized cancellation).
- Icarus RTL vs exact oracle: 3072/3072 supported CLOSE outputs and flags matched.
- Full Wave32 collector -> significand multiplier -> RNE CLOSE: two directed transactions passed with tags, masks, three RF responses, output stalls and retirement.
- One-lane bounded CLOSE accumulator + RNE packer generic Yosys synthesis: 5708 cells, 6070 wire bits, 162.65 MB peak memory. No physical technology mapping.
- Initial CI run https://github.com/sushxnthd/vektor/actions/runs/38430763342 FAILED at synthesis after numerical and Wave32 RTL passed. Missing default for a temporary shift variable in reused CLOSE accumulator; fixed and rerun successfully.

## Workload-mix counterexample (software-modeled, seed 149901)

CLOSE-only finishing is not a general FP32 FMA engine. The frozen 40,965-active-FMA synthetic operand-stream probe produced:

| Stream | CLOSE-eligible / active | Fraction |
| --- | ---: | ---: |
| Positive vector FMA | 0 / 8192 | 0.00% |
| Signed vector FMA | 2159 / 8192 | 26.36% |
| Evolving-accumulator GEMM fragments | 1042 / 8192 | 12.72% |
| Cancellation positive control | 8192 / 8192 | 100.00% |
| Divergent masked signed stream | 2081 / 8197 | 25.39% |

These are generated operand streams, not real GPU traces. Zero eligibility for same-sign vector FMAs is structural. Prioritize FAR/special completion rather than optimizing CLOSE alone. Retain CLOSE as an optional bypass only if later equal-resource PPA/throughput tests support it.

**Not passed:** full IEEE-754 FMA, general FAR and NaN/Inf/zero cases, scoreboard, writeback, full-tile timing/area/power, RTX 5090-class gates.

**Scientific novelty:** not established. CLOSE/FAR specialization is prior art; generic cells are not silicon area.

## Reproduced CI and frozen corpus

Run 38431443467 passed all existing tests and saved raw artifact 11831750427. SHA256 of the 3072-vector corpus: 0415e5e4230da07b0dbe5623488b335163d3e22fb899a9516adf9e349c3dae3f. Next CI adds one-lane integrated synthesis and logic-depth reporting; those results are pending.

## Timing-proxy caution

Run 38431668216 passed generic synthesis and arithmetic tests, but hierarchical Yosys ltp reported repeated loops at the top-level mr ready connection. Hierarchical path-length output (close rounder 145, close accumulator 95, multiplier 41) is NOT a clock-frequency estimate. Next run flattens the integrated design, applies check -assert, and recomputes ltp to distinguish hierarchy artifacts from a genuine combinational cycle. Do not promote the timing gate until that passes.
