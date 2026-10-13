# V143 ARCHITECTURE — 2026-10-13

**Decision:** retain duplicate RF-read coalescing as an operand-collector requirement, but do NOT choose a monolithic 3x1024-bit response mux or a single serialized response bus as the canonical design without an integrated PPA/throughput comparison.

**CI-verified isolated RTL:** 3-response coalescer 9286 generic cells, 6144 muxes, 12-cell path; 1-response valid-only tagged bus 81 generic cells, 7-cell path; passthrough 6 generic cells, 1-cell path. CI runs 38381018667 and 38381219776 passed 3456 abstract cases and 1600 directed/randomized full-Wave32 RTL test vectors across two topologies. Generic logic proxy only, no mapped timing, power, SRAM or silicon.

**Simulated bandwidth penalty:** single response bus vs unlimited slows 1x/2x/3x source-multiplicity workload classes by 3.5836x / 2.9544x / 1.4856x mean respectively; 3-response bus mean 1.2362x / 1.2201x / 1.0x. Synthetic 432-run model; 72 metamorphic exact reference checks. Neither implementation is an established Pareto winner.

**Architecture direction:** explore bank-local or small-cluster response multicast (2-4 concurrent vectors) with per-bank arbitration and registered collector capture. Measure wiring/mux/valid control separately and integrate real IEEE-754 FMA. Keep hardware cost and throughput budgets matched.

**RTX 5090 capability gates:** FP32 INCONCLUSIVE; tensor INCONCLUSIVE; graphics/raster INCONCLUSIVE; ray INCONCLUSIVE; memory INCONCLUSIVE; cache/NoC INCONCLUSIVE; software INCONCLUSIVE; physical PPA INCONCLUSIVE; reproducibility PARTIAL (isolated RTL/model only). No 5090-class claim.

**Next decisive action:** integrate RF coalescing + producer multicast + FP32 + scoreboard and measure mapped PPA and realistic kernels.
