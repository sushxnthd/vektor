# Vektor-109 preregistration (2026-10-11, before experiment)

Type: DISCRIMINATION, CAPABILITY-BUILDING, SURPRISE. Software-only evidence.

H1: old validator accepts a duplicate atomic event while replay changes final memory.
H2: old validator accepts at least one mixed-PC, oversized or empty wave.
H3: strict once-only/32-lane/same-PC-op checker rejects those malformed schedules but accepts original warp/locality/packed plans.
H4: independent C++ validator matches Python on unseen seeds and mutations.

Fixed sets: 128 discovery seed 1082026; 64 holdout seed 1089001; 24 surprise seed 1083333 (11.1%); test duplicate/drop/out-of-range/empty/oversize/swap/merge/reverse/repeated-lane mutants. Residual = legacy accepted but strict rejected; no GPU cycle or physical predictions.

Competing explanation: old checker may have been intended solely to validate ordering, and a hardware decoder may reject malformed waves. Do not claim hardware bug. Cheapest next discriminator: actual Vortex SimX LSU lane traces.
