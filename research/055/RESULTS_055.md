# Vektor-055 validated RTL and generic synthesis — 2026-10-09

**GitHub Actions PASS:** https://github.com/sushxnthd/vektor/actions/runs/37887628553 at commit `78451cbda8f153c48634766d1367a7d103efd839`. Evidence artifact: https://github.com/sushxnthd/vektor/actions/runs/37887628553/artifacts/11597216650 .

## Verified RTL / SYNTHESIZED generic cells
- **40/40 Icarus Verilog differential tests PASS**, 1,500 cycles each, **60,000 RTL cycles** across 0/1/2/3-source masks, source holes, alias fanout, tagged returns, invalid/stale returns, and randomized backpressure. The Python reference and separately structured external trace checker also passed.
- **Yosys generic synthesis PASS**, `check -assert` reports zero problems.
- DEDUP=0: **2,175 generic cells**. DEDUP=1: **2,371 generic cells**, +196 (**+9.01%**). Both have 278 flip-flop cells (72 DFFE + 206 DFF); the six additional FF relative to Vektor-054 correspond to the two 3-bit source masks.
- Compared with Vektor-054 fixed-three-source synthesis, masking adds 36 cells (+1.68%) without dedup and 48 (+2.07%) with dedup. These are **technology-independent generic cell counts**, not physical area, timing, frequency, power or GPU throughput.

## Source inspection: static PTX virtual-register identities
Pinned public 14-kernel hand-written BPF PTX: 272 eligible instructions, 564 register-source uses, 10 repeats (1.773%), 20 three-source instructions, zero three-source repeats. A compiled vector-add PTX fixture: 6 eligible instructions, 13 uses, zero repeats. Combined **10/577 = 1.733%** repeat uses in this narrow static subset. No physical register or dynamic frequency is inferred.

## Software simulation (not RTL throughput)
40 exploratory 1,500-cycle reference traces: PTX-static-uniform 856 -> 865 completions (+1.05%); deliberately injected 25% alias 737 -> 811 (+10.04%); 50% alias 737 -> 878 (+19.13%); zero-alias control 803 -> 803.

64-seed exploratory holdout (3,000 cycles per seed per policy): 27,464 -> 27,657 completions (**+0.703%**), 40 wins / 19 losses / 5 ties. Paired-seed bootstrap 95% interval +0.371% to +1.044%, reflecting synthetic-seed variation only. Reads 57,229 -> 56,619 (−1.066%).

## Falsification and next gate
A 25% synthetic alias injection is not a defensible typical workload assumption for the audited PTX corpus. Masked RTL functionality is validated, but **dedup hardware ROI is unproven**; its +9.01% generic control-cell overhead cannot be compared directly with whole-GPU throughput. No area/timing/power or RTX 5090-class claim.

**Single next decisive action:** obtain dynamic physical-register alias histograms from several independent compiled kernels and test 4/8/16-slot banked collectors under equal-port controls with mapped PPA.
