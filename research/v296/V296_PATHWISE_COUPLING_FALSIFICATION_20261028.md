# V296 pathwise closed-loop coupling falsification (2026-10-28)

**Result: negative, exactly as preregistered.** This is a synthetic scheduler/operand-bank experiment, not routed physical evidence or GPU performance. The protocol was committed first at `12a1e842`, followed by the executable independent-model experiment at `41633e37`. Run `node research/v296/v296_pathwise_coupling.js --self-test` or run without flags for the complete per-seed JSON.

## Independent checks
- **104,976** exhaustive canonical four-request cases, covering 16 validity masks and 3^8 operand-bank assignments, produced zero serial/pairwise admission disagreements and zero two-read-port violations.
- **100,000 synthetic cycles per contestant** (5 preregistered regimes × 4 fixed seeds × 5,000 cycles) yielded identical **per-cycle accepted-wave ID traces**, identical read traffic and identical collision rejections. The stateful closed-loop scheduler includes 32 warps, four issue slots, deterministic counter-hashed external readiness/bank streams, a round-robin cursor, per-warp next-ready latency and a shared issue-bandwidth ceiling.
- A deliberately incorrect same-bank pairwise mutant **was detected** by the preregistered hotspot negative control. No outcomes or regime parameters were retuned.

| Frozen regime | B | Latency | Seed 1701 admitted waves | Pair compatibility | Pair overlap | V296/serial accepted-trace equality |
|---|---:|---:|---:|---:|---:|---|
| Uniform high readiness | 4 | 1 | 18,744 | 0.7924 | 0.2076 | exact |
| Concentrated same-bank hotspot | 4 | 1 | 6,005 | 0.1010 | 0.8990 | exact |
| Shared issue-port bottleneck | 1 | 2 | 5,000 | 0.7512 | 0.2488 | exact |
| Low readiness, longer latency | 4 | 5 | 14,308 | 0.7525 | 0.2475 | exact |
| Temporal hotspot/readiness bursts | 2 | 3 | 7,877 | 0.4842 | 0.5158 | exact |

Compatibility is measured as no shared bank between the first two selected wave pairs, not as an independently measured real GPU workload distribution. Other fixed seeds 1709, 1723 and 1741 also passed exact pathwise checks; the script emits their complete measurements.

## Predictive boundary and proof scope

For the **same single-slice resources, clock, latency, priority order and external trace**, serial and V296 make the same admission decision on every cycle. Assuming the same initial scheduler state, equality of grants implies equality of accepted waves, next-ready states and cursor at the next cycle; induction gives equality for every future cycle, including arbitrarily correlated arrivals. Therefore

`G_issue(p_compat, overlap, B, occupancy, control) = 1`

for every regime within this matched architecture model. The parameters strongly change *absolute* throughput but cannot change the ratio. This is a rigorous negative boundary conditional on the model, not a novel positive-law mechanism. The simulator is an independent finite-trace check of the induction premises, not a proof of arbitrary RTL-level equivalence.

A physical advantage could still exist through independently established energy, achievable clock frequency, or area-driven slice packing; none has been demonstrated. At the frozen 30,000 um2 tile ceiling both original integrated routed implementations fit only one slice. The ongoing symmetric upstream physical repair is the sole bounded remaining V296 experiment. If it fails the preregistered matched gate, retire V296 rather than rebranding admission-equivalent arbitration as throughput improvement.

**Evidence tier:** synthetic coupled model + exhaustive small-bank enumeration. **Not:** extracted-RC repair success, SRAM timing, measured power, GPU benchmark throughput, or RTX 5090 equivalence. Kernellum PR #119 and holdouts untouched.
