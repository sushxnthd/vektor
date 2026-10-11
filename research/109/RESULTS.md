# Vektor-109 result

Host-model verification, 2026-10-11. Preregistered 128 discovery, 64 holdout, 24 minimally guided probes (11.1%).

Across 2,564 mutated schedule checks, 581 malformed schedules passed the previous dependency-only checker but failed the new full-interface validator. The independent C++ and Python implementations agreed on all 2,564 cases. Six directed/exhaustive Python tests and one trace-schema audit test passed. All 648 original warp/locality/packed schedules were accepted.

Counterexample: duplicate execution of an atomic increment changes final memory from 4097 to 4098 in the deterministic host model, but the legacy checker accepts it. This falsifies using that checker alone as a complete Wave32 schedule-validity certificate. It is not evidence of a hardware RTL bug.

At Vortex upstream commit 7fe19369587c087f902c3e2bc2add612aa910a95, trace_csv.py omits per-lane effective addresses and memory-order epochs. Instrument SimX LSU before claims about actual GPU memory coalescing.

No GPU speedup, power, area or clock measurement. RTX 5090-class gates remain INCONCLUSIVE. Full experiment and preserved V108 source are in the separately delivered reproducibility archive.
