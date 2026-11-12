# Physical-time queue boundary (2026-11-03)

Evidence tier: exact arithmetic and local deterministic toy simulation, **not** RTL, silicon, GPU IPC, or a surviving V317 mechanism. Previous V317 electrical and matched-area falsifications remain binding.

For steady offered work rate λ (requests per baseline clock period), baseline service capacity b per baseline period, candidate service c per candidate period, and candidate period multiplier 1+δ, the fluid steady-state throughput ratio is

`R = min(λ,c/(1+δ)) / min(λ,b)` for λ>0.

Consequences: when λ≤min(b,c/(1+δ)), R=1, so service headroom cannot improve throughput. For λ≥max(b,c/(1+δ)), R=c/[b(1+δ)], so a candidate with c=b and δ>0 **loses** throughput. For a capacity-doubling zero-cost oracle at δ=1%, saturated upper-bound R=200/101, but low demand R=1. This is an optimistic oracle ceiling, not realizable scheduling throughput. The finite-horizon clock-edge checker uses identical absolute-time arrivals for both variants and explicitly conserves pending requests. A 100-time-unit saturated example completes 100 at b=1, 99 at c=1 and 1% slower clock, and 198 at c=2 and 1% slower clock. A 20-request burst drains fully under both b=1 and c=2, yielding equal total work.

Prospective workload classifications: **predicted no-win** λ≤b with no baseline queue; **conditional predicted win** λ> b and c/(1+δ)>b, provided sustained backlogs and no downstream bottleneck. These are analytical classifications, not unseen-workload validation. A future test must use ordered real-kernel arrivals, real physical clock/port constraints, and a strongest equal-resource hardware control. No V317 promotion or RTX-5090 claim is permitted.

Local checker `finite_horizon_queue_boundary.py` was executed and passed before GitHub persistence. Separate GitHub-hosted execution remains unverified.
