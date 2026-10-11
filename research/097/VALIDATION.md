# Vektor-097 validation — 2026-10-11

32,768 bounded legal traces: V096 9,088 output-stability violations; source-lock zero. Four independent C++17 replays matched 16,384 cycles. Four Icarus RTL runs matched 16,384 cycles (Actions run 38099557590). Yosys 0.33 generic synthesis passed with 950 cells for default four-source configuration (run 38099463468). These are not physical PPA or GPU throughput.

Negative result: first RTL CI failed because signed -1 comparison suppressed overdue selection. Corrected and rerun.

Exploratory 256-case sweep: 32 minimally guided probes, 6,070 legacy violations, zero repaired; both policies admitted 207,059 synthetic beats. Legacy is protocol-invalid.

Next: compose V097, V095 FIFO and V094 FINAL path; verify reset, loss, duplication, backpressure. RTX 5090-class gates INCONCLUSIVE. $0 personal spend.
