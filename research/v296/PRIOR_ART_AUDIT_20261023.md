# V296 priority and novelty audit (2026-10-23)

## Position
V296 is a physical implementation experiment on the Vektor register-file admission path, **not** a newly invented GPU arbitration principle. Pairwise equality checking, bank-conflict detection and priority admission are ordinary digital-logic structures. Current evidence is a 18.04% Nangate45 *mapped controller-cell-area* reduction relative to the best tested one-hot implementation at B=16, issue slots=4, 2 RF ports/bank. That observation alone is not a world-class architecture result or a GPU-level gain.

## Closely related research (verified bibliographic leads)
1. Sparsh Mittal, "A Survey of Techniques for Architecting and Managing GPU Register File," IEEE TPDS 27(6), 2016. Survey of performance/energy/reliability RF techniques. https://www.ornl.gov/publication/survey-techniques-architecting-and-managing-gpu-register-file
2. Ipoom Jeong et al., "Triple-A: Early Operand Collector Allocation for Maximizing GPU Register Bank Utilization," IEEE Embedded Systems Letters 16(2), 2024. DOI 10.1109/LES.2023.3307622. Optimizes GPU operand collectors and RF utilization. Different mechanism, relevant system-level comparison.
3. "BOW: Breathing Operand Windows to Exploit Bypassing in GPUs," MICRO 2020. DOI 10.1109/MICRO50266.2020.00084. RF bypass and collector design; does not establish V296 novelty.
4. Mohammad Sadrosadati et al., "Enabling High-Capacity, Latency-Tolerant, and Highly-Concurrent GPU Register Files via Software/Hardware Cooperation," 2020. https://arxiv.org/abs/2010.09330. Includes register-bank conflict avoidance via renumbering; relevant alternate solution.
5. Chunyang Gou and Georgi N. Gaydadjiev, "Addressing GPU On-Chip Shared Memory Bank Conflicts Using Elastic Pipeline," IJPP 41, 2013. DOI 10.1007/s10766-012-0201-1. Addresses *shared memory*, not register-file arbitration; cite as adjacent work only.

## Priority conclusion and falsifiers
- No novelty claim for pairwise comparison or bank-aware scheduling.
- Narrow potential contribution: reproducible crossover coefficients for area, timing and switching energy of two equivalent RF admission circuits across bank count, issue width, physical placement and fanout, plus a verified tile-level benefit when the issue path is actually limiting.
- Strongest equal-resource control must be optimized and timing-driven, not merely the existing one-hot RTL; include a compiler/logic-optimized comparator alternative if available.
- If clean STA, placed interconnect or realistic wire/load assumptions erase benefit, retire V296. If no measured energy or frequency advantage survives, do not open sealed workload holdouts.
- No evidence of RTX 5090 equivalence, post-route fmax, total GPU area reduction or novel GPU scheduling.
