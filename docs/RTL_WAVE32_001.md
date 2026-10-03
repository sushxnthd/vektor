# RTL-WAVE32-001 — Scheduler topology and first synthesizable V-Tile control blocks

## Scope

This gate moves Vektor beyond simulator-only scheduler assumptions. It implements and verifies three four-wide Wave32 scheduler topologies plus the RF bank arbiter in synthesizable SystemVerilog:

1. fixed 4 x 8-wave partitions;
2. idealized 32-wave global four-wide arbitration;
3. limited work stealing: one primary issue per 8-wave partition plus at most one backup issue from each donor partition.

The global design is a hardware comparison point, not the selected architecture. The limited-steal design is the current candidate.

## Frozen evidence

- source head: `0a3e16bf7aa35b4021b3e038b58bb033e8440d27`
- RTL Actions run: `37130920341`
- RTL artifact digest: `sha256:32f67f0d55c59986b42e4ae309619ed55245a69d31ab8701e6713a6361aaf4ab`
- simulator Actions run: `37130920361`
- scheduler-topology artifact digest: `sha256:06a347fb5c239e4fa62dd22f5676eaa9e784bd931faf14478c3b55fcafeb7294`

All scheduler simulations, RF-arbiter simulation, generic Yosys synthesis steps, simulator tests, and benchmark capture passed on the frozen head.

## Generic synthesis result

Yosys 0.33 generic cell counts:

| scheduler | generic cells | vs fixed | vs global |
|---|---:|---:|---:|
| fixed 4x8 | 444 | 1.00x | 8.22% |
| limited steal | 1,223 | 2.75x | 22.65% |
| global four-wide | 5,399 | 12.16x | 100% |

The RF-bank arbiter separately maps to 1,321 generic cells.

These counts are technology-independent synthesis proxies. They are **not** transistor counts, mm^2, timing closure, or power measurements.

## Scheduler-topology model

On deterministic synthetic readiness traces:

| trace | fixed 4x8 utilization | limited steal | global upper bound |
|---|---:|---:|---:|
| balanced | 100% | 100% | 100% |
| four ready waves in one partition | 25% | 50% | 100% |
| two rotating donor partitions | 50% | 100% | 100% |
| lopsided memory-return proxy | 46.875% | 68.75% | 100% |

The global scheduler therefore recovers all modeled issue-width loss but costs roughly 12.2x the generic logic of fixed partitioning. Limited stealing recovers a substantial fraction of the synthetic loss while using about 22.7% of the global scheduler's generic cells.

## Current architecture decision

**Promote limited stealing to the current V-Tile scheduler candidate.**

Reason: the fixed design has a large readiness-clustering cliff, while the full global arbiter has an excessive generic logic penalty at this stage. Limited stealing provides a materially better provisional utilization/cost tradeoff.

This decision is provisional. It must survive:

- timing-aware synthesis / place-and-route proxies;
- RF-bank and operand-cache interaction;
- dependency-aware workload traces rather than abstract readiness only;
- memory-return clustering from the explicit hierarchy;
- fairness/starvation testing;
- comparison against published/open scheduler baselines before any novelty claim.

## Claim boundary

Supported: Vektor now has synthesizable scheduler and RF-arbitration RTL, and under the frozen synthetic topology model limited work stealing is a better provisional utilization/generic-cell tradeoff than either rigid 4x8 partitioning or the implemented full-global baseline.

Not supported: real application speedup, novelty, physical 2.56 GHz operation, area, energy, power, process-node feasibility, complete V-Tile functionality, or RTX 5090 equivalence.

## Next decisive gate

Build an integrated issue-control slice using the limited-steal scheduler + RF arbitration, then add operand/register state and an IEEE-754 FP32 FMA lane backend. Verify RTL behavior against the simulator and use a public, standards-tested FMA implementation only as a comparison/reference; Vektor's architecture-level claims must not depend on copying proprietary GPU RTL.
