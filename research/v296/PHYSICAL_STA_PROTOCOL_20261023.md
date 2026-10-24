# V296 electrical discriminator: preplacement gate (2026-10-23)

V296 has **one** active architecture mechanism and draft PR #13. V287 remains retired. The prior Nangate45 cell-area advantage was 3,098.368 vs 3,780.126 um^2 (18.0353% reduction). This is NOT a measured timing or energy improvement.

This run adds a three-way *matched-netlist* experiment: original V-Tile, strongest optimized decode-after-select one-hot control, and pairwise V296. Identical Nangate45 Liberty, Yosys mapping, 2.0 ns reference clock, 0.15 ns I/O budgets, 0.04 ns input transition and 0.005 pF output load. Uniform per-net lumped RC proxy is varied (0.002/0.004/0.008 pF; 0.1/0.2/0.4 kohm). These values are sensitivity assumptions, NOT extracted wire parasitics. A successful run cannot certify placement/routing or real silicon fmax. Check worst setup slack, Liberty max-capacitance and max-transition violations, then compare the strongest control. Missing paths or missing metrics invalidate the run.

**Falsification:** if V296 does not exceed the strongest control's constrained timing in every RC case, it has no frequency-based workload win under the current hypothesis. Retire unless a separately measured equal-resource energy benefit survives. Do not open frozen workload holdouts before electrical review.

**Predictive boundary, not yet validated:** with identical issue throughput I waves/cycle and shared non-issue ceiling M waves/sec, T(f)=min(f I,M). Thus G=min(f_pair I,M)/min(f_control I,M), and G=1 whenever M<=min(f_pair,f_control) I. With issue-control area fraction a=A_issue/A_tile, the maximum area-only tile reduction is 0.180353 a, not 18% of the entire GPU. No RTX 5090 equivalence is implied.

Reproduce: .github/workflows/v296-sta.yml, research/v296/run_sta.sh, research/v296/sta_mapped.tcl, research/v296/analyze_sta.py. Review raw STA reports and exact tool SHAs; subsequently require placed/extracted SPEF, buffering, dynamic switching/power and unseen workloads.
