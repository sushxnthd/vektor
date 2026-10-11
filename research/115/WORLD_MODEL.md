# Vektor-115 world model

| State | Claim | Evidence / caveat | Next test |
|---|---|---|---|
| KNOWN (host-model) | FIFO joining repeated (uuid,hart,tag) records under output reordering can misattribute VA→PA | V115 directed, seeded and independent exhaustive controls | Actual Vortex traces |
| KNOWN (source audit) | Vortex MMU may replay misses and allow hit-under-miss | Pinned upstream sim/simx/mem/mmu.cpp | Instrument and compile |
| KNOWN (source audit) | Vortex coalescer merges lane requests into memory-line requests and forwards a representative hart_id | Pinned upstream sim/simx/mem/mem_coalescer.cpp | Correlate with coalescer masks |
| BELIEVED | Translation-point paired logging is more reliable than external FIFO matching | Synthetically exact by construction, patch anchors checked | Compile/run patched SimX |
| CONFLICTING | V114 needs post-MMU physical addresses; post-MMU requests are aggregate not lane-level | V114 world model and Vortex coalescer source | Record upstream lane membership at coalescer |
| FALSIFIED | (uuid,hart,tag) FIFO matching is sufficient for unambiguous translation correlation | V115 counterexample and independent enumeration | Preserve as negative control |
| ANOMALOUS | Identical address-tag fields can correspond to distinct requests; egress order may differ from ingress | Model deliberately adversarial; real incidence unknown | Measure repeated-key and reordering rates |
| UNTESTED | Patched Vortex compiles and emits correct trace on real kernels | No full simulator compilation or execution | CI build and execution |
| UNTESTED | Cache-aware cohort scheduling improves workload time after translation, migration and occupancy costs | No hardware/cycle validation | Actual SimX trace + equal-budget model |

## Bottleneck cluster

V110–V115 repeatedly expose **trace and dependence provenance** as the common bottleneck. Elevate reliable end-to-end memory provenance to a first-class capability-building target, rather than treating each aliasing defect as an independent GPU architectural gain.

## Single next decisive action

Compile the pinned SimX MMU probe and capture real translated requests with page-table and coalescer controls. Do not claim physical memory traffic or lane completeness from MMU records alone.
