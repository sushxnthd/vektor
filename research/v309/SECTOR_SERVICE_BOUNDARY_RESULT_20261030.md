# V309 conditional sector-service pressure boundary result (2026-10-30)

**Decision:** the equal-resource ideal fixed-address coalescer remains **NO-WIN**. No new GPU mechanism is promoted. This is a mathematically checked *conditional service-roofline sensitivity*, not measured GPU throughput or new architecture novelty.

## Evidence and execution

- Frozen [protocol](SECTOR_SERVICE_BOUNDARY_PROTOCOL_20261030.md) committed at `a20e39f` **before** the implementation.
- [Executable rational model](sector_service_boundary.py) committed at `c95f8db`.
- [Hosted GitHub Actions #41012765180](https://github.com/sushxnthd/vektor/actions/runs/41012765180): **PASS**. Includes 729 independent total-service-time oracle comparisons, monotonicity checks and invalid-input refusal.
- Previously audited inputs: 3,937,565 active SASS rows; 1,586,194–1,595,385 32-byte sectors **conditional on an unverified historical tracer-source model**. These span 50,758,208–51,052,320 conditional sector-service bytes, or approximately **12.891–12.965 bytes per dynamic instruction**. These are not measured DRAM bytes.

## Frozen predictive boundary

For I instruction rows, S sectors, assumed sector-service bandwidth B bytes/cycle, assumed issue ceiling P instructions/cycle, hypothetical sector reduction r and issue-time penalty h:

`C = min(P/(1+h), B*I/[32*S*(1-r)])`.

The modeled issue-versus-sector boundary occurs at `B/P = 32*S/I`. The input interval places it between **12.891 and 12.966 service bytes per instruction**. This ratio describes an *aggregated, hypothetical service model*, not an actual GPU roofline; 11 previously explored applications were pooled.

| Frozen regime | Assumptions | Conditional gain at both sector endpoints | Outcome |
|---|---|---:|---|
| Synthetic predicted win | B=8, P=1, r=25%, h=5% | +33.333% | Matches prediction |
| Synthetic predicted no-win | B=32, P=1, r=25%, h=5% | -4.7619% | Matches prediction |
| Strongest ideal fixed-address coalescer | B=8, P=1, r=0, h=0 | **0%** | NO-WIN |
| Fixed-address coalescer with issue penalty | B=8, P=1, r=0, h=5% | 0% (memory ceiling masks issue cost) | NO-WIN |

The 25% reduction is **invented as a counterfactual sensitivity parameter**, not observed, not synthesized and not an implemented hardware design. Passing a synthetic prediction does **not** constitute unseen-workload validation. For unchanged memory addresses, an ideal coalescer already covers the minimal set of sectors; r=0 by construction. Adding logic cannot create a sector-count gain.

## Limitations and next kill gate

The archive's actual producer identity remains unverified. The sector count does not establish cache misses, DRAM transactions, stall cycles, GPU bandwidth utilization, occupancy, timing, power or performance. The model ignores cache reuse, coalescer implementation, latency hiding, memory-level parallelism and per-workload phase variation. A pooled ratio is not a prediction for any one Rodinia workload.

**Do not promote** a layout-changing mechanism from this synthetic 25% reduction. Next substantive work must acquire a *validated independent cycle/counter reference* or authenticate source provenance, then derive and freeze **per-workload** predictions before holdout evaluation. Existing V287/V296 and other retired hardware avenues remain retired; no unsupported RTX 5090 claim. Kernellum #119 unchanged.
