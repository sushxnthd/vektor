# V317 pairwise bank-credit arbiter: source-pinned RTL/formal/synthesis result (2026-11-01)

## Protocol, source and evidence tier

The [frozen protocol](FROZEN_PAIRWISE_BANK_CREDIT_PHYSICAL_CHALLENGE_20261101.md) was committed at `c428fa2` before the RTL, testbench, synthesis or results. The source-pinned successful [hosted run #41283774756](https://github.com/sushxnthd/vektor/actions/runs/41283774756) used commit `92eff95704e14c4c9e76fcae836fd6e609a1f2dc`. The independent duplicate [run #41283771350](https://github.com/sushxnthd/vektor/actions/runs/41283771350) also passed. These results are **generic Yosys logic synthesis**, **independent RTL simulation**, and **combinational SAT equivalence**. They are NOT standard-cell area, routed delay, dynamic power, real GPU IPC, or physical signoff.

## Functional and formal result

- The independent two-read-port-per-bank oracle passed **20,545** RTL configurations: four phases × (4,096 exhaustive two-bank vectors + 16 directed 16-bank vectors + 1,024 seeded full-bank random vectors), plus one reset/wrap check. The oracle compared **four** implementations: original fixed, pairwise fixed, original rotating, pairwise rotating. All passed.
- Yosys `equiv_make; equiv_simple; equiv_status -assert` proved **all four output bits** of the pairwise fixed implementation equivalent to the original fixed arbiter over **all possible 16-bank inputs**, not just sampled test vectors. The proof log reports **4 proven, 0 unproven** equivalence cells.
- The rotating wrapper was independently tested across all four phases, but **sequential formal equivalence for the rotating wrappers has not been proven**.
- An initial hosted run failed because an all-zero initial stimulus left the source combinational `always @*` block untriggered in Icarus, producing X. The testbench was repaired by priming a nonzero vector before the exhaustive sweep. Preserve failed [run #41283568545](https://github.com/sushxnthd/vektor/actions/runs/41283568545); it was a testbench initialization issue, not an observed non-equivalence.

## Matched generic synthesis

All four implementations use the same Yosys 0.33 `read_verilog -sv; synth -flatten -top; stat; ltp -noff; write_json` sequence on the same hosted environment.

| RTL implementation | Generic cells | Logic levels | Flip-flops | Max generic net sink fanout |
|---|---:|---:|---:|---:|
| Source fixed priority | 1,321 | 49 | 0 | 49 |
| **Pairwise fixed priority** | **272** | **22** | 0 | **11** |
| Source rotating priority | 1,613 | 58 | 2 | 49 |
| **Pairwise rotating priority** | **557** | **31** | 2 | **41** |

Both frozen generic-area predictions **survived**. Relative to the corresponding source RTL, pairwise fixed saves **79.41%** generic cells and 27 logic levels; pairwise rotating saves **65.47%** generic cells and 27 levels. These are substantial *implementation proxy* reductions, not measured silicon area or timing. The reduced levels are not a measured clock gain.

**Strong comparator correction:** once the fixed-priority control receives the same pairwise optimization, rotating priority costs **557/272 = 2.0478×** its cells, **31 vs 22** levels, and two extra flops. It is misleading to compare optimized rotation against the old unoptimized fixed control. The earlier source-only 1.221× rotation premium is no longer the relevant equal-optimization comparison.

## Mechanistic explanation and predictive cost hypothesis

The source implementation synthesizes 16-bit `used_once`/`used_twice` occupancy masks and variable bank decoders. The pairwise implementation tests whether each new operand bank matches any previously granted physical operand. With `S` request slots and `B` banks, the comparator count is `2S(S-1)` bank-ID equalities (24 at S=4), each comparing `ceil(log2 B)` bits. A **hypothesis**, not yet an unseen-width validated law, is comparator-side logic scaling roughly as `O(S² log B)` versus bank-mask-side `O(SB)` plus decode/mux cost. Standard-cell mapping and wider S/B sweeps must establish the real boundary.

## Workload and tile-level consequence, strictly conditional

The pairwise RTL produces **identical grants** to the source policy. At matched clock, port count and issue width, its intrinsic scheduler throughput gain is therefore **exactly 1.000×**. Its value is a possible hardware-cost reduction, not a new scheduling mechanism. The previous frozen stressed synthetic service result was **64,784 rotating vs 60,899 fixed** completed requests after warmup, `g=1.06379415`, with oldest-first already at **64,774**; this is fairness versus a weak fixed-priority control, not novelty.

For a hypothetical fixed arbiter occupying fraction `a` of a baseline tile, and unknown achieved clock ratio `c=f_rot/f_fixed`, the **conditional** throughput-per-tile-area ratio for optimized rotating versus optimized fixed is

`E = g*c/[1 + a*(557/272 - 1)]`.

At stressed synthetic `g=1.06379415`, break-even requires `c > 0.94003` at `a=0`, `c > 0.94988` at illustrative `a=0.01`, `c > 0.98928` at illustrative `a=0.05`; at `a=0.10`, equal clock is insufficient. At equal clock, the illustrative maximum `a` is **0.06088**. **None** of these assumed tile fractions, clock ratios or GPU throughput values is measured.

## Decision and remaining physicality ladder

**Keep the pairwise bank-credit implementation as a strong, lower-cost source-equivalent RTL baseline.** It materially improves generic synthesis proxies and passes a full combinational fixed-priority equivalence proof. **Do not promote rotating priority as a novel architecture mechanism**: a simple oldest-first scheduler nearly matches its synthetic fairness gain, while the optimized rotating control still costs more than the equally optimized fixed control.

Next gates: sequential formal proof of rotating phase behavior; mapped standard-cell timing and fanout; load/RC sensitivity; matched area/clock for rotating, oldest-first and fixed; real bank-access traces; power proxies; integrated tile-level area and performance; unseen B/S width validation. Kill any performance claim erased by the strongest controls or clock/area costs. No RTX-5090-equivalence claim is supported.

Reproduction: `.github/workflows/v317-rf-pairwise.yml`, `research/v317/rtl/rf_bank_pairwise_credit.sv`, `tb_rf_bank_pairwise_credit.sv`, and `parse_rf_pairwise_cost.py`. The workflow preserves source SHA, simulation/formal logs and all four JSON netlists even on failure.
