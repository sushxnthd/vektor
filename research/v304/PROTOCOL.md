# V304 prospective protocol: static warp-colored RF bank layout

Date: 2026-10-29. Candidate: static per-warp bank coloring `bank=(reg+2*(warp_id%8))%16`, with register storage laid out accordingly at allocation. This is **not** runtime register remapping. One candidate only.

## Rationale and scope
The baseline V-Tile model uses `bank=reg%16`, creating artificial cross-warp hot-bank collisions. Before claiming a new scheduler mechanism, test whether cheap static layout coloring removes the bottleneck. Compare against the **strongest equal-state alternative** `bank=(reg XOR (2*warp_id))%16`, and the uncolored baseline. Both colored policies use warp-ID wiring and a small combinational decode; XOR is potentially cheaper than an adder. No silicon claims.

## Frozen experiment
- Deterministic, lossless per-warp, in-order, round-robin issue model: 32 warps, 128 two-source FP32 instructions each, 4 issue slots/cycle, 16 banks, 1 RF read port/bank, cache disabled. Identical logical instructions across controls.
- Predicted win H1: fixed paired adjacent source registers across all waves; candidate should reduce bank collisions against uncolored modulo.
- Predicted no-win H2: seeded independent random source registers per instruction; candidate should not outperform the strong XOR coloring control by 5%.
- Additional H3: aligned register pair with 2 ports/bank; H4: low occupancy 4 warps; H5: phase-shifting pairs.
- Holdout seeds: 901..920; do not inspect and then tune. Metric is completed logical instructions per cycle, including all issued instructions, not a GPU IPC claim.
- Candidate survives only if H1 throughput exceeds the strongest equal-state XOR control by >=5% and H2 is not worse by >2%, and there is no new unmodeled data movement. If H1 fails, retire without RTL. Report every seed, sensitivity and no-go.
- Invariant: per-warp instruction order and exact instruction count conserved. Independent reference oracle checks mapping permutations, conflict counts and retirement.
- Boundary law to test: for a candidate group of k warps with bank-demand sets S_i, same-cycle feasibility is max_b sum_i 1[b in S_i] <= ports. A probabilistic predictor must estimate the distribution of S_i intersections; a mean bank occupancy alone is not enough.
- No novelty claim until prior-art audit: bank swizzling/coloring and operand collectors are established GPU/processor ideas.

Physicality gate if it survives: clocked RTL mapping and bank decoder, equal-resource synthesis against XOR, timing/electrical checks with realistic fanout and wires, workload trace transfer and tile-level consequence. No RTX-5090 equivalence.
