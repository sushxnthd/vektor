# V292 first public RTL and synthesis gate — 2026-10-23

Source branch: `research/v292-sparse-return-overlay`
CI run: https://github.com/sushxnthd/vektor/actions/runs/39874100797
Raw evidence ZIP: https://github.com/sushxnthd/vektor/actions/runs/39874100797/artifacts/12468110251
Artifact digest: sha256:e43aec870bd126fb42574087cdc644d43fb4d652b3c650cbb7abd43a23aa6ffb

## Observations (not architectural speedups)
- Icarus RTL smoke: **6000/6000** lane integrity, credit and mask checks passed.
- Independent Python oracle: **50000/50000** random admission cases passed; frozen holdouts **unopened**.
- Yosys 0.33 generic `synth`: **2247 generic cells**, including **1024 $_MUX_**, **1074 $_ANDNOT_**, **48 $_AND_**, **32 $_NAND_**, **33 $_NOT_**, **31 $_OR_**, 3 $_ORNOT_, 2 $_NOR_. Zero `check` problems. No mapped area, critical path, max-cap, slew or switching power.
- Training mask boundary, separate from RTL: q=0.2 gives observed 0.27065 disjoint pairs versus predicted 0.2708192 (200k trials); q=0.5 gives 0.000115 versus predicted 0.00010045 (200k trials). This is *pair eligibility*, not throughput.
- Two frozen holdout mask densities (q=0.08 and q=0.70) and one collector-port adverse case remain unopened.

## Mandatory next physical discriminator
Before claiming even a tile-level modeled benefit, inventory actual L1 return bus and collector write-port widths, and synthesize a same-resource conventional sector/packing controller with identical 1024-bit bus, two tags, two masks, 2 destination credits, 2-entry queue and lane mux budget. At least 1024 generic muxes suggest nontrivial area/timing overhead; **not** characterized evidence. Check whether existing cacheline sector returns even expose independent per-lane valid masks. If no, retire V292 without more wrapper work.

Do not extrapolate a two-return/beat smoke result to warp issue, FP32 or memory throughput. No V-Tile modification or RTX 5090 comparison is justified.
