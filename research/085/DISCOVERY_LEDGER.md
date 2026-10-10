# Vektor-085 Discovery Protocol V2 world model

**KNOWN within bounded model:** explicit shared RF bank-port conservation, RAW/WAW exclusion, coherent writeback invalidation, exact commit accounting and sequential final-value agreement; 75 Python tests and independent C++ trace checker on three cases.

**BELIEVED:** opportunistic read/write port borrowing may exploit idle bank bandwidth; physical area and power are not modeled.

**CONFLICTING:** increasing read opportunities can worsen total completion time via altered issue and future writeback bursts. Example 8 waves x128 spread: shared3=490 vs split2+1=401, yet some 16-wave regimes reverse.

**FALSIFIED:** a fixed four-cycle lookahead read throttle generalizes (96-case holdout: 17 wins,31 losses,48 ties).

**ANOMALOUS:** fixed 2-read cap exactly restores 401 cycles from 490; shared3 WB stalls 2392 vs split 49 in the selected trace. Conditional writeback-slot reservation reduces to 395 with no queued WB stalls.

**UNTESTED:** physical port costs, RF SRAM macros, issue-time reservation critical path, energy, area, frequency, compiler-generated GPU workloads, graphics, tensor, ray, memory controller, RTX 5090 equivalence.

### Experiments

E85-A CAPABILITY-BUILDING / DISCRIMINATION: finite bank arbitration + coherent reference model; cold single-bank bound p/3. Residual shared2 0.6654 vs theoretical 0.6667 = -0.0013 instruction tokens/cycle. Alternative: unmodeled bypass/cache coalescing would change RF demand. Cheapest next: RTL arbitration checker.

E85-B SURPRISE: 89-cycle slowdown with more flexible ports in one spread trace; exact fixed read-cap ablation isolates scheduling/writeback interaction. Alternative: rotating issue policy artifact; no independent cycle replication. Cheapest next: alternative scheduler and compiler trace.

E85-C EXPLOITATION failure: predictive read throttle fails holdout; preserve as negative result, do not tune posthoc and claim generality.

E85-D DISCRIMINATION / conditional EXPLOITATION: future writeback reservation 490->395 cycles, zero queued writeback stalls, 47/96 holdout wins but 17 losses. Residual +9.4 percentage points beyond preregistered 10% improvement threshold in selected trace; not broad adoption. Competing explanation: synthetic burst alignment, uncosted reservation table. Cheapest next: synthesizable reservation table and workload-class prediction.

Failure clustering 076–085: incomplete shared-resource accounting, correctness hazards, and phase-sensitive scheduling; elevate unified RF/issue/writeback model to first-class research target. Prior-art auditor: operand collectors, bank arbitration and scoreboards already known (GPGPU-Sim). No novelty claim. Replicator: independent C++ trace replay, not timing replication.

**Foothold:** workload-conditional WB reservation is a reproducible simulation-level mechanism, not an established physical improvement. **5090-class gates:** all INCONCLUSIVE.

**Single next action:** canonical simulator integration and RTL/free-flow verification before optimization claims.
