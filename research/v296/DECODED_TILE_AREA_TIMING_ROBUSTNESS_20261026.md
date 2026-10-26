# V296 decoded tile: prospective area/clock robustness and kill boundaries (2026-10-26)

**Status:** A deterministic algebraic sensitivity/falsification experiment, committed while the matched routed experiment [40359299905](https://github.com/sushxnthd/vektor/actions/runs/40359299905) is running. **Not** an extracted-RC result, GPU throughput measurement, physical tile, or new arbitration mechanism. V296 remains the sole provisional mechanism; V287 remains retired.

## Frozen inputs and exact reproducibility

The input is [BANK_DECODE_PAIRED_PRECTS_RESULT_20261026.json](BANK_DECODE_PAIRED_PRECTS_RESULT_20261026.json), from run 40337484954. It is expressly **pre-CTS estimated-parasitics** evidence, and its serial contestant **does not include** the independently optimized fifth-stage repair. The script [v296_decoded_tile_robustness.py](v296_decoded_tile_robustness.py) rejects a different evidence tier, provenance, or missing fifth-stage limitation, and uses Decimal arithmetic for integer area fit.

Run from the repository root:

```bash
python3 research/v296/v296_decoded_tile_robustness.py --self-test
python3 research/v296/v296_decoded_tile_robustness.py --evaluate
```

The output is `research/v296/DECODED_TILE_ROBUSTNESS_RESULTS_20261026.json`. The local self-test and sweep passed before commit; these are **not** hosted RTL or routed checks. The 32-point area and 36-point conditional workload grids are reproducible and are not fitted to future routed outcomes.

## Finding 1: the proposed extra slice is fragile to candidate-specific area overhead

At the frozen pre-CTS checkpoint, serial area is **17,301.969635 µm²/slice** and candidate area **16,089.542143 µm²/slice**. Holding the 17-serial area budget fixed, the maximum fractional candidate-only overhead permitting 18 candidate slices is

```text
epsilon_c,max = 17 A_serial / (18 A_candidate) - 1
              = 0.0156130581117556553 = 1.5613058112%.
```

This is an **exact integer packing threshold conditional on single-slice pre-CTS areas**, not a measured multi-slice routing threshold. The same-area budget accommodates 18 candidate slices at 0%, 1.5%, and 1.56% candidate-specific overhead, but only 17 at 1.6% and 2%. A change in serial overhead moves the boundary; the sweep includes 0%, 0.5%, 1%, and 2% serial overhead and eight candidate overhead values. The strongest fifth-stage serial area could invalidate this pre-CTS reference altogether.

## Finding 2: ideal resource capacity is not a GPU speedup

For identical 2-cycle dependency latency, four issue slots per slice, 16 banks with two read ports per bank, and resident warp count W, a **conservation ceiling** is

```text
Q_ideal(N,W) = min(4 N, W/2, 16 N).
```

The ratio of these ceilings is **not a mathematical upper bound on actual speedup** because either architecture can underutilize its ceiling differently. It is only an idealized reference, not a scheduler simulation.

| Frozen sensitivity case | 17 serial capacity ceiling | Candidate capacity ceiling | Ratio of ceilings at equal clocks |
|---|---:|---:|---:|
| W=32, 18 candidate slices | 16 | 16 | 1.0000 |
| W=180, 18 candidate slices | 68 | 72 | 1.0588 |
| W=180, 17 candidate slices (1.6% candidate-only overhead) | 68 | 68 | 1.0000 |
| W=180, 18 candidate slices, both limited by 25 waves per baseline-clock interval | 25 | 25 | 1.0000 |

The hypothetical +5.882% ideal-capacity ratio is **not** a measured throughput gain. It requires an extra physically realizable slice, sufficient occupancy, no binding shared bandwidth cap, equal feasible clocks, and comparable utilization. Earlier matched synthetic schedulers have already shown that nominal issue capacity can be unattainable due to bank conflicts. A 2% longer candidate period reduces the hypothetical 18/17 ratio to **1.03806**, but this remains an ideal-capacity calculation, not physical clock data.

For given *actual* admission rates q_s and q_c and feasible period ratio r=T_c/T_s, the proper workload boundary with a shared physical-time cap M is

```text
G = min(q_c/r, M) / min(q_s, M) - 1.
```

This script varies r=0.95, 1.00, 1.02 and M in {unbounded, 25}, using **ideal capacities** in place of q only as a transparent conditional sensitivity exercise. The next workload evaluation must replace both q values with matched, independently checked workload admissions and r with physically feasible clocks. A ratio of ideal capacities must never be promoted to an observed positive law.

## Finding 3: the pre-CTS timing guard has effectively zero robustness margin

The candidate pre-CTS setup slack is +0.050206 ns against a frozen +0.050000 ns guard: **0.206 ps** margin. An *algebraic* adverse setup-slack perturbation of +0.207 ps fails the guard. This is not a fitted wire-delay coefficient and not a prediction of post-CTS delay. The sweep probes adverse perturbations from 0 to 50 ps; only extracted post-route STA can determine the real sign and magnitude.

## Prospective decision before routed results

1. **Physical kill:** If the decoded candidate fails the frozen routed +50 ps setup guard, nonnegative hold, zero cap/slew/DRC, or route completeness, reject the decoder as a viable physical repair at 3.5 ns. Do not retune constraints after seeing results.
2. **Matched-control gate:** Even if candidate passes, no relative Pareto claim without the strongest fifth-stage serial and independent extracted-RC audit.
3. **Area reinvestment kill:** If final *replicable tile* area and routing overhead do not support an extra candidate slice under equal consumed resources, discard the extra-slice benefit hypothesis. Do not infer a tile from single-slice pre-CTS area.
4. **Frozen predicted-win regime:** Occupancy-rich, distributed-bank, bandwidth-unsaturated, dependency-tolerant work can benefit only if actual admissions, feasible clocks, and full tile resources satisfy G>0 on unseen workloads.
5. **Frozen predicted-no-win regimes:** Binding shared physical-time bandwidth, low occupancy with equal feasible clocks and identical admissions, or candidate-specific area overhead that erases the extra slice without compensating clock/issue advantage. Preserve negative outcomes.
6. **Scope:** No SRAM macros, power measurement, thermal analysis, complete tile layout, or RTX-5090 equivalence. Kernellum PR #119 and its holdouts remain untouched.

**Verdict:** This sweep narrows the survival envelope but does not establish V296 as physically feasible or world-class. The decisive next evidence is the already-running matched post-CTS extracted-RC pair.
