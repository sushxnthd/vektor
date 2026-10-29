# V303 port-budget prospective protocol (2026-10-29)

## Locked question
Can a finite-port, version-coherent operand-cache update path beat the simple write-invalidate controller, once cache-write conflicts and register-bank contention are modeled? This extends V303; it is **not** a new mechanism. The previous ideal-update policy is an unpriced upper bound.

## Implementation constraints
An independent value-carrying simulator must enforce (1) cache hits return the current register version, (2) source reads precede destination writes, (3) a destination update consumes a physical update port, (4) when update ports are exhausted the entry is invalidated rather than silently updated, and (5) the same wave scheduling, register banks, and cache capacity are used for each control. Initially restrict to FP32 instructions; no load-completion coherence claims.

## Frozen regimes and predictions (before implementation/results)
- H1 read-mostly reuse: invalidation and limited update should tie, since source registers are rarely overwritten.
- H2 alternating dependent FP32 overwrites: a one-port update can reduce some RF reads, but might not improve cycles due to scheduler/eviction feedback.
- H3 write-heavy high occupancy: one-port contention should force invalidations; a four-port idealized alternative may recover reads but has a larger hardware cost.
- H4 no-cache capacity: all policies must tie exactly.

Compare invalidate, one-port opportunistic update, four-port update, and free ideal update on identical wave traces at cache capacities 0, 8, 64. Report cycles, RF reads, bank stalls, update demand, granted updates, invalidations and overflow. Preserve all negative results.

## Predeclared survival rule
A one-port design must improve total RF reads by >=5% versus invalidate in H2 without increasing cycles by >1%, and must not worsen cycles by >1% in H1 or H3. This is a *necessary but insufficient* gate; further require a matched RTL implementation, synthesis, routed timing/electrical checks, power proxies and realistic workloads before any GPU benefit claim. If it fails, retire V303; do not retune on opened regimes.

## Predictive boundary
For per-cycle resident-destination write demand D and P update ports, granted updates <= min(D,P), and forced invalidations >= max(0,D-P). RF-read savings additionally depend on future reuse and eviction, so no monotonic throughput benefit is presumed. Evaluate predicted update fraction against measured, then test whether the proxy predicts performance on unopened workloads.

No GPU IPC, frequency, area, power or RTX-5090 equivalence is established by this protocol.
