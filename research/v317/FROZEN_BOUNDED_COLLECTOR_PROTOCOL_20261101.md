# V317 bounded-collector physicality challenge: preregistered protocol (2026-11-01)

**Status:** frozen before implementing or running the new bounded-collector solver. This continues the existing V317 measurement/falsification branch and PR #34. No new architecture is promoted.

## Question
Do the idealized staged-service capacity gains survive a finite operand-collector budget when both the strongest baseline and the hypothetical read-elimination candidate have identical collector slots, read ports, and completion width?

## Exact model
Three independent single-read-port banks A/B/C. Instruction classes AB, BC, CA with counts (a,b,c). Baseline reads AB/BC/CA; candidate *hypothetically* removes B from AB, reading A/BC/CA. Every instruction is ready at time zero. At the beginning of each cycle an optimal scheduler may admit any waiting instruction, subject to K in-flight collector entries (including those already admitted); admitted operands can be read in that cycle. At most one read per bank per cycle, arbitrary cross-cycle staging, and up to two newly completed instructions at cycle end. Completed instructions vacate collector entries only after the cycle. No eviction, forwarding, cache hits, dependency stalls, or admission/control/clock penalties. Each instruction requires each specified bank exactly once. Both designs get the **same** K and bank ports; no hidden extra collector capacity.

Compute minimum service cycles with an exhaustive shortest-path state-space search, not a greedy heuristic. State must preserve counts of unadmitted classes and active per-instruction remaining operand masks; canonicalize identical instructions. A second independent validator must check every returned labeled cycle trace for admission/collector limits, bank exclusivity, exactly-once reads, and completion width. Verify shortest paths by an independent bounded-depth reachability oracle on reduced worlds, not merely replaying the same solver.

## Predictions frozen before implementation
- Win: (a,b,c)=(2,2,0), K=2, baseline 4 cycles, candidate 2 cycles, gain 2.000x. This remains **hypothetical read elimination**.
- No-win: (2,2,2), K=4, baseline 4 cycles, candidate 4 cycles, gain 1.000x.
- Transfer: (2,1,0), K=2, baseline 3 cycles, candidate 2 cycles, gain 1.500x.
- Tight occupancy stress: (2,2,0), K=1, baseline 8 cycles, candidate 6 cycles, gain 1.333x.
- Under K=1, the exact predicted law for any nonempty (a,b,c) is G=2(a+b+c)/(a+2b+2c). This is **service-cycle** gain only.

Unopened transfer worlds (do not use for tuning): (3,2,1) at K=2; (1,3,2) at K=3; (3,0,3) at K=2. Report whatever the exact oracle finds. Sensitivity sweep: K=1..6 on all frozen regimes, plus exhaustive reduced worlds a,b,c in 0..2 at K=1..3 (excluding empty). If an exact solver is too expensive, preserve the partial result and explicit timeout; never substitute optimistic bounds as attained throughput.

## Falsification and limitations
Any violation of an independent trace check or exactness audit invalidates the corresponding claim. For finite K, the earlier unlimited-collector capacity envelope is only a lower bound. Even a positive exact result is *not* a physically implemented mechanism, measured GPU IPC, power/timing signoff, or a novel result. A strong real baseline must also include register-cache reuse and compiler rematerialization. Hardware promotion requires an actual mechanism with matched RTL/PPA, realistic dynamic bank mapping, control and wire/load sensitivity, and a prior-art audit. If control, timing, occupancy, or strong equal-resource baselines erase the gain, kill the candidate.

This is a falsification of model assumptions, not a claim of RTX 5090 equivalence.
