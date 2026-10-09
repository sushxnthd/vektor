# Vektor-057 world model addendum

KNOWN: FIFO-ordered ages make first-urgent selection equivalent to maximum-age urgent selection. Same-flow generic cells: 546 -> 277 (49.27% reduction); RTL differential and cross-policy tests passed.

BELIEVED: ordered ages can be maintained efficiently in a real collector, subject to queue compaction and saturation.

CONFLICTING: improved aggregate IPC does not guarantee fairness; pure near-done starves a long instruction in an adversarial model.

FALSIFIED: age-guard control overhead is negligible; optimized selector still uses 277 cells versus FIFO's 73.

ANOMALOUS: a simple order invariant nearly halves combinational control cells.

UNTESTED: complete queue, formal invariant, mapped PPA, dynamic compiled traces, GPU capability gates.

Next: tagged collector and invariant proof.
