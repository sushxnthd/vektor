# Vektor-111 host-model results (2026-10-11)

1955/1955 independent Python/C++ comparisons matched: 192 discovery x 6 plans, 96 holdout x 6, 36 surprise x 6, and 11 directed controls.

Compared with V110, V111 admitted 59 additional discovery, 24 holdout, and 8 surprise schedules in the explicitly scoped abstract model. The 178 admitted random reversed plans preserved namespace-qualified byte-memory replay. A directed V110 counterexample accepted a same-PC mixed-CTA wave, which V111 rejects.

The surprise generator initially produced an out-of-range access near 2^64. It was repaired to retain valid address ranges without changing seeds; the original failed assertion is preserved in the downloadable evidence archive.

These are HOST SOFTWARE MODEL results, not Vortex trace validation, GPU execution speedups, RTL synthesis, frequency, area, power, or RTX 5090 equivalence. Full experiment, independent C++ source, raw records, preregistration and SHA256 manifest are preserved in the reproducibility package. The repository quickcheck is a smaller directed regression, not a rerun of all 1955 comparisons.

Single next decisive action: capture actual Vortex SimX LSU addresses, memory spaces, CTA IDs and synchronization events and validate namespace identity.
