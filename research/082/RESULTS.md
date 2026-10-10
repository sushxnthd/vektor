# Vektor-082 results (2026-10-10)

Status: software-model simulation only. No RTL/silicon claims.

Vektor-081 modeled operand-ready rates above four instructions/cycle. Vektor-082 adds a finite four-wide issue interface and a bank-aware operand-order option.

Experiments: 200 controlled, 30 exploratory (13.0%), 80 holdout comparisons. Independent C++17 model agreed on 640/640 numerical comparisons across 160 configurations. Fixed-order unlimited-issue backward compatibility with Vektor-081 passed.

With 24 collectors, 2 operands, balanced banks and pipelining: 4.790 operand-ready/cycle becomes 3.992 issue/cycle. With 40 collectors and 4 operands: 5.698 becomes 3.988. These are modeled rates, not GPU performance.

Bank-aware vs fixed-order (100 controlled pairs): 23 improvements, 3 regressions, 74 ties. Holdout (80): 23 improvements, 2 regressions, 55 ties. Maximum benefit: 378 to 364 cycles for 1200 synthetic instructions (3.7%).

Interpretation: The previous operand-ready rate is not sustainable issue throughput. Bank-aware read reordering has workload-specific gains and occasional reversals. Physical cost, writeback coherence and instruction traces remain untested. All RTX 5090-class gates INCONCLUSIVE.

Next: integrate four-wide issue boundary into canonical V-Tile simulation; validate operand-version correctness and bank-aware arbitration in RTL.
