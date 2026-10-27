# V296 dynamic D16: prospective mapped-area transfer result (2026-10-27)

## Original immutable evidence
- Frozen prediction: [DEEP_BANK_DYNAMIC_MAPPED_TRANSFER_AND_D16_FREEZE_20261027.md](DEEP_BANK_DYNAMIC_MAPPED_TRANSFER_AND_D16_FREEZE_20261027.md), committed at `7d653169`, **before** the D16 mapped run.
- [GitHub Actions run 40542155911](https://github.com/sushxnthd/vektor/actions/runs/40542155911), immutable head `831ec79865d4c0b85f8bc25904737eb7c73a702b`; six jobs successful (D4/D8/D16 RTL and D4/D8/D16 matched mapped synthesis).
- D16 mapped ZIP artifact 12752960026, SHA-256 `f1733131d283e6cedcc96cddd3070773a9d9d98f2ec16f6eb04d7a6c9140b008`; D16 RTL artifact 12750287978, SHA-256 `29ed1b595edc447c621fe68644c1a4b733d42e2648b22cb423cfa5c0980dbe37`.
- Same-run D4 mapped artifact 12752126503, SHA-256 `cdeee83a0b3e22f0734c3c107181ef2a9231fec1c71c52d55d73bc592cfd28c6`; D8 mapped artifact 12751094117, SHA-256 `efe40ce43c0d4ad37a7a83902ccb566e671633b59287631e2f38c4f3d255e8d4`.
- Original ZIPs were downloaded and SHA-256 verified; independent parser confirmed same source RTL and Nangate45 library SHA across all depths, Yosys 0.9, `check -assert` zero problems, and D16 2048-cycle RTL oracle pass with all 16 word addresses covered. The independently checked `nangate.lib` bytes matched the provenance hash.

## Frozen prediction vs observed D16 mapped synthesis

| Contestant | Frozen D16 prediction (um2) | Observed D16 area (um2) | Relative prediction error |
|---|---:|---:|---:|
| V296 pairwise | 26,736.458 | 27,861.638 | +4.2084% |
| Equal-RF serial `PREDECODE=0` | 28,674.800 | 28,998.256 | +1.1280% |

**Frozen model gate PASS:** each error is below the predeclared 15% relative threshold, and pairwise mapped area remains smaller than serial. This is a narrow success for the *two-point mapped-area extrapolation*, not a routed or workload-level positive law.

| Depth | V296 area | Serial area | Saving vs serial |
|---|---:|---:|---:|
| 4 | 12,960.584 | 13,835.990 | 6.3270% |
| 8 | 17,552.542 | 18,782.260 | 6.5472% |
| 16 | 27,861.638 | 28,998.256 | **3.9196%** |

**New adverse finding:** the frozen D16 saving prediction was 1,938.342 um2, but measured saving is only **1,136.618 um2**. The prediction overstated the *advantage* by **41.3613%**. V296's absolute area saving is nonmonotonic across D4/D8/D16 (875.406, 1229.718, 1136.618 um2), falsifying any unqualified monotonic-saving extrapolation. The two-point area model's stated pass criterion remains satisfied; do not silently strengthen or rewrite it after outcomes.

## Decision boundary and tile consequence

For the same D16 cell library, let `Hc` and `Hs` be **additional, unmeasured** candidate and serial physical overhead in um2. The mapped area ordering survives only if

`Hc - Hs < 1136.618 um2`.

This is an *area break-even condition*, not a predicted routed penalty. At the illustrative 30,000 um2 mapped-only budget, both contestants fit **one** slice and neither fits two. Thus **zero extra integer slices** and **no measured tile throughput advantage** follow from this result. The stronger independently routed-feasible serial implementation has still not been established.

## Scope and next hard falsification

Evidence tier: **SHA-verified RTL + Yosys mapped synthesis only**. The 8-bit flop-array RF with two dynamic read ports/bank is not a GPU RF macro. `ltp -noff` crosses sequential boundaries and reports thousands of loops; it is **not STA**, a clock-frequency measurement, or extracted-RC evidence. There is no routed D16 closure, realistic wire/load, matched feasible serial, bandwidth, occupancy, workload IPC, power, or RTX-5090 equivalence.

The next experiment must physically close both architectures under identical floorplan, clocks, port counts, wire/RC constraints and realistic RF depth. A candidate-only feasible result is insufficient. If the differential physical overhead erases 1,136.618 um2 or either contestant fails frozen electrical checks, the mapped proxy cannot support a matched physical win. Freeze workload win/no-win regimes before evaluating unseen workloads; do not open sealed holdouts.

V296 pairwise bank admission remains the **sole provisional mechanism**. V287 and static fixed-word readout stay retired. Preserve draft PR #13, negative results, and Kernellum PR #119 unchanged.
