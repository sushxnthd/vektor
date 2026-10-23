# V296: mapped STA audit falsifies apparent frequency gain (2026-10-23)

Source: https://github.com/sushxnthd/vektor/actions/runs/39915799933
Artifact: 12484649187 (21 files, all nine STA logs and three mapped Verilog netlists).
Source commit: 0cc67dd243f260f36845085b69d47cf071b68bed.

## What passed

* Nangate45 Liberty blackbox import repaired the strict Yosys mapped-driver check.
* Three-way RTL test: 2,048 randomized cycles passed.
* All three standard-cell mapped netlists were generated and loaded into OpenSTA.
* All nine uniform-RC cases completed and produced parsable reports.

## Decisive methodological falsification

The previous summary computed a 1.2786x **apparent** pairwise-to-control frequency ratio from `report_worst_slack -max` (nominal critical-budget proxies 3.755002 vs 4.801229 ns). **This is not a valid issue-frequency result.** The top timing paths in all three mapped controllers start at `rst_n` and terminate in **asynchronous recovery checks**, not the register-bank admission data path. A smaller reset recovery delay cannot be presented as a faster GPU issue path.

The reference 2.0 ns clock also fails timing for all variants: nominal all-path worst slack is -3.000501 ns (original), -2.801229 ns (optimized control), and -1.755002 ns (pairwise). These figures are *not* characterized fmax.

## Electrical violations (nominal RC)

| Mapped variant | Max-slew violators | Max-capacitance violators |
|---|---:|---:|
| Original | 987 | 39 |
| Optimized equal-resource control | 979 | 35 |
| Pairwise V296 | 698 | 41 |

**No variant passes electrical signoff.** The earlier analyzer incorrectly accepted STA as successful despite hundreds of violations. Therefore V296 has **not** passed the clean-electrical or valid issue-timing gate. The 18.04% mapped cell-area result remains a preliminary block-level area measurement.

## Corrected discriminator

The updated `sta_mapped.tcl` records the full reset-inclusive worst slack separately, then excludes reset-starting paths from the **issue data-path** comparison, retaining reset recovery as an independent signoff obligation. The updated `analyze_sta.py` rejects missing/async data paths and fails closed if any mapped variant violates slew/capacitance limits. Even if data-path timing improves, a red electrical gate cannot be called a physical win.

**Decision:** V296 remains the sole active mechanism *provisionally*, with the timing-gain claim withdrawn. Next experiment must obtain valid issue-path STA and then equal-budget resizing/buffering or placement to eliminate electrical violations. Retire V296 if the corrected matched-resource advantage disappears or cannot meet electrical limits. Frozen workload holdouts remain sealed. No tile-level throughput, power, or RTX 5090 equivalence claim.
