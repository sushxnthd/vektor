# Vektor-101 results: composed RTL cancellation and tag reuse

Run date: 2026-10-11. Research branch: research/composed-rtl-101.
Verified commit before coverage assertion: 64d3aef7a37812d997cc567377aa0641bfa97b66.
CI: https://github.com/sushxnthd/vektor/actions/runs/38113268411

**Evidence type: RTL simulation + generic Yosys synthesis. Not silicon PPA.**
The differential test compares two structurally identical return networks
with V094 FINAL-wins versus V099 cancel-wins consumers.

| Sources | FIFO depth | Copies | Tag bits | Grants = FINALs | Cancel/FINAL races | Same-cycle cancelled tag reuses | Stalled cycles |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 4 | 3 | 3 | 562 | 215 | 180 | 1560 |
| 2 | 4 | 3 | 3 | 562 | 215 | 6 | 1560 |
| 8 | 4 | 3 | 3 | 562 | 213 | 185 | 1560 |
| 4 | 8 | 3 | 3 | 562 | 215 | 180 | 1560 |
| 4 | 4 | 1 | 3 | 1669 | 645 | 93 | 1526 |
| 2 | 4 | 3 | 1 | 507 | 197 | 167 | 1522 |

All six configurations passed RTL conservation, policy delta,
stall stability, post-drain occupancy and same-trace equivalence checks.
This is bounded directed verification, not an unbounded formal proof.
The paired V098 and V100 generic Yosys synthesis (default parameters)
reported 3299 versus 3292 generic cells, respectively. Seven cells
fewer in this flow is not an area or timing advantage claim.

## Anomaly: instrumentation false negative

The first testbench revision reported **zero** same-cycle tag reuses
despite many cancellation/FINAL races. This was a testbench observation
error: it compared the post-edge return tag with a newly registered
grant tag. Sampling the return tag *before* the edge and comparing it
to the post-edge grant corrected the instrumentation. The rerun then
observed 6-185 same-cycle cancelled reuses per configuration.
The original zero-reuse result is **FALSIFIED**, not discarded.

## Prediction and residual

- Preregistered grants==FINALS, FINALS==complete+stale and beats==COPIES*FINALS:
  observed exactly in all six configurations (residual zero).
- Preregistered old_complete - new_complete == live FINAL/cancel collisions:
  observed exactly (residual zero).
- Preregistered identical handshakes and pending/live masks:
  observed exactly in all six configurations.
- Exploratory reuse coverage prediction: nonzero under pressure;
  observed 6-185 per configuration after correcting the sampling point.

## World model update

- **KNOWN:** The composed RTL passed six bounded directed simulations
  and generic synthesis under a trusted flush, one FINAL, and eventual drain.
- **BELIEVED:** The cancellation-wins composition generalizes to more
  adversarial workload traces under the same protocol contract.
- **CONFLICTING:** FINAL-wins is correct under a different API contract.
- **FALSIFIED:** Post-edge tag sampling is sufficient to detect same-edge
  reincarnation; the original testbench silently missed it.
- **ANOMALOUS:** Return-fabric topology changed the number of same-cycle
  reuses without changing total admitted transactions in the tested window.
- **UNTESTED:** Full formal composition, reset/quiescence proof, physical PPA,
  GPU writeback workloads, and all RTX 5090-class gates.

**Single next decisive experiment:** Build a formal/bounded composition
harness with explicit source-quiescence and FINAL-uniqueness assumptions;
then test an intentionally duplicated FINAL and an untrusted flush_ack as
negative controls. These assumptions currently sit outside the RTL.

Cost: $0. No 5090-class gate advanced.
