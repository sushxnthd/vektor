# Vektor-107 world model (2026-10-11)

KNOWN: 106's 128B grouping proxy is not an NVIDIA 32B sector metric; 32B coalescer request counts are 88->72 in the controlled model. Cold ideal-cache read misses are 20->20. 96 paired issue-order cases yield 0 versus 5 miss regressions (step versus group).

BELIEVED: a cache-aware grouping gate might avoid regressions on real workloads; unverified.

CONFLICTING: fewer coalescer requests can coincide with unchanged or increased L1 misses.

FALSIFIED: 128B-group proxy reduction implies equal 32B-sector savings; lower L1 read demand necessarily means lower DRAM traffic.

ANOMALOUS: seven finite-cache regressions in primary discovery/surprise; five in post-discovery confirmation under group-major order.

UNTESTED: real Vortex LSU traces, cross-warp regrouping legality, timing, cache bank conflicts, MSHRs, NoC, RTL, PPA.

FOOTHOLD: reproducible measurement correction and cache/issue-order boundary, not a GPU speedup.

SINGLE NEXT DECISIVE ACTION: instrument Vortex SimX LSU and cache events; compare grouping on real traces with identical cache budgets and legal lane-migration controls.
