# Vektor-106: compiler-visible cohort hypothesis (2026-10-11)

This branch extends Vektor-105 with an executable, source-derived, host-side
memory-sector test for a persistent SGEMM row cohort. **Not GPU execution,
compiler-generated traces, RTL, synthesis, or GPU speed measurements.**

## Preregistered prediction and outcome

For the hypothetical 2D SGEMM thread layout, 128-byte sectors, even W warps,
aligned row pitch and K<=32: persistent row grouping saves exactly
`2*W*(K+1)` sector requests at a cost of `16*W` lane migrations.
112/112 independent structured holdouts satisfy both formulas. 16 surprise
probes deliberately break assumptions: only 2/16 match the sector law and
6/16 the migration law. This **falsifies unrestricted generalization**.

The strong control is conventional warp grouping with identical per-lane
memory expressions and the same 32-lane cohort capacity.

## Crucial negative result

Across 1,890 fixed-resource **non-overlap accounting proxies**, row cohorts
win 689, lose 1,110, tie 91. The proxy
`ceil(sectors/B)+ceil(moved/M)+setup` is NOT a GPU timing model.
Fewer memory sectors are insufficient to claim a speedup.

Run: `python3 research/106/standalone.py` (Python 3.10+, no dependencies).

Source expressions from public Vortex regression SGEMM:
https://github.com/vortexgpgpu/vortex/blob/7fe19369587c087f902c3e2bc2add612aa910a95/tests/regression/sgemm/kernel.cpp

Complete cross-language source-derived trace suite, 144 Python/C++ event
matches, 128 C++/Python sector matches, BFS write-hazard vetoes, preregistration,
world model, target ledger and raw data are in the V106 reproducibility bundle.
The branch's standalone script reproduces the main quantitative result.

## Decision

Do not promote the row cohort to Vektor-1A RTL. First collect real Vortex
simx per-PC/per-lane memory traces and actual launch geometry; then validate
legality, migration/RF/NoC overhead and equal-resource cycle performance.
Vektor-1A remains a hypothesis. RTX 5090-class gate remains INCONCLUSIVE.
