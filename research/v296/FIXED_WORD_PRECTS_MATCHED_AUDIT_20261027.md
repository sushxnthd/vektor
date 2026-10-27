# V296 fixed-word RF: independently SHA-pinned matched pre-CTS result (2026-10-27)

**Evidence tier: paired OpenROAD pre-CTS global-route estimated parasitics, NOT post-CTS, extracted-RC signoff, SRAM feasibility, or GPU performance.**

## Original artifacts

GitHub Actions [40457696916](https://github.com/sushxnthd/vektor/actions/runs/40457696916) completed functional RTL equivalence, four-way mapped synthesis, pairwise pre-CTS and serial pre-CTS jobs.

- Candidate ZIP artifact 12716756605, SHA-256 `cebe917377f0a3195a43e9bdb3917a0b8036e198ed8444250d7fca019c10f349`.
- Serial ZIP artifact 12717298019, SHA-256 `6455f4b21faf1919c2b38b5d9887bb4942f98b061ec9ec6901628adaaa53b3c3`.

Both original ZIPs were independently downloaded, their SHA-256 digests matched GitHub's artifact records, and common physical constraints, tool versions, input hashes, Tcl, generator manifests and completion markers matched. Local independent audit replay and corruption rejection passed. The companion machine-readable result and SHA-pinned checker preserve reproducibility.

## Matched pre-CTS measurements

| Metric | Fixed-word V296 pairwise | Fixed-word serial |
|---|---:|---:|
| Fourth-stage area (µm²) | **12,806.5700** | 15,103.7458 |
| Estimated setup slack (ps) | **+230.183** | −193.882 |
| Estimated hold slack (ps) | +112.255 | +113.217 |
| Capacitance violations | 0 | 0 |
| Slew violations | 0 | 0 |
| Frozen +50 ps candidate pre-CTS setup guard | **PASS** | FAIL |

V296 has **15.2093% less fourth-stage pre-CTS area** and **424.065 ps more estimated setup slack** than the fixed-word serial contestant. This is an apples-to-apples fixed-word comparison, but **the independently optimized fifth-stage serial repair is excluded**; the serial timing failure cannot be treated as defeat of the strongest control.

## New physical sensitivity and falsification boundaries

1. Candidate setup has only **180.183 ps of net deterioration budget** before failing the frozen +50 ps guard. CTS, extracted wire RC and electrical repair may consume this margin. The previous *different* decoded density-0.35 design suffered 276.388 ps degradation between post-CTS global-route and extracted timing; that is a caution, not a transferable prediction.
2. Conditional on equal feasible clocks and per-slice replication, **18 candidate slices versus 16 serial slices** tolerate **4.8333% additional candidate-only per-slice area overhead** relative to these pre-CTS areas. **19 versus 16** already exceeds budget by **0.6842%** at zero overhead. These are algebraic area boundaries, not tile layouts or demonstrated throughput.
3. At identical issue grants and clock, the fixed-word refactor itself provides **zero admission-throughput gain**. Any V296 benefit requires independent bank-admission workload evidence or a physically validated equal-budget/clock consequence.
4. The RF proxy has **exactly two words per bank**. Fixed read ports wired to word 0/1 are not transferable to realistic deep SRAM/register-file banks. Production claims require deeper-bank transfer and matched port, wire, power and timing sensitivity.

## Decision

The fixed-word V296 implementation **passes the preregistered candidate pre-CTS gate**, so a matched routed trial is justified, **but no physical signoff is established**. The next trial must use the strongest fifth-stage serial control, unchanged 3.5 ns / 2× RC constraints, CTS, detailed routing and extracted SPEF. Reject the repair if candidate setup < +50 ps, hold < 0, any cap/slew/DRC violation remains, or final area > 30,000 µm². Do not relax thresholds or infer clock gain from pre-CTS slack.

V296 is the sole provisional architecture mechanism. V287 remains retired. Keep PR #13 draft, preserve Kernellum PR #119, sealed workload holdouts, and all negative evidence. No RTX-5090-equivalence claim.

Reproduce with original ZIPs and `research/v296/fixed_word_prects_sha_audit.py` (SHA-pinned independent checker).