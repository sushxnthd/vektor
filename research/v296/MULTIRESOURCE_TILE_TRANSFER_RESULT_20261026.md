# V296 multi-resource tile transfer: frozen synthetic validation (2026-10-26)

**Evidence tier:** independently generated request-level **synthetic** transfer of a conditional mapped-area packing law. **Not GPU performance, routed tile signoff, measured power, or a new architecture mechanism.**

## Prospective design
Preregistered predictions, seeds, tolerance, workload generator and no-win controls in commit `8eb467e3`, **before** writing or running the new simulator. Executable committed in `7f2b21f`; hosted reproducibility workflow in `33d0d00`. No real GPU workload holdout was accessed. V296 remains the sole mechanism, V287 retired.

The mapped balanced-return areas previously measured on Nangate45 are 9286.592 um² V296 and 9844.926 um² independently optimized serial. An area budget of 17 serial slices can **hypothetically** accommodate 18 V296 slices, but no such tile has been placed or routed. At identical clock and slice count, both arbiters admit the same waves.

## Predictive boundary law
For a hypothetical resource-matched tile with n slices, mean admitted waves q per active slice-cycle, occupancy u, control overhead o, period T, bytes/wave m, shared byte bandwidth B and shared RF read throughput R, the useful rate (waves/ns) under an explicitly idealized work-conserving fluid-server assumption is:

`W = min(n*q*u/[T*(1+o)], B/m, R/2)`.

Candidate wins only when its unconstrained offered rate exceeds serial **and** serial is not already saturating the shared limiting resource. A 17-to-18 replication opportunity tolerates a candidate period increase of strictly less than `18/17 - 1 = 5.88235%` before losing its unconstrained rate advantage. This threshold is conditional on physical packing and independent feasible clocks; it is not a measured frequency margin.

## Prospective validation
Two unseen, frozen seeds (41213, 49531) generated 20,000 cycles each. Each active slice independently generates four candidate waves with valid probability 0.8 and intra-wave same-bank probability 0.2. A concrete-bank admission oracle enforces at most two reads per bank, **without using q as input**. Shared bandwidth and read-port limits are imposed by an independently coded persistent-backlog fluid server. Both contestants see paired first-17-slice workloads; V296 hypothetically has one additional slice. Occupancy u=0.85 and overhead o=0.03 were frozen. The q reference is the previously independent exact law, 2.992340240625.

| Frozen regime | Predicted useful-rate gain | Seed 41213 observed | Seed 49531 observed |
|---|---:|---:|---:|
| 100 GB/s, 100 reads/ns, equal 3.5 ns clocks | +5.88235% | +5.90433% | +5.90303% |
| 10 GB/s bandwidth limit | 0% | 0% | 0% |
| 4 reads/ns shared port limit | 0% | 0% | 0% |
| Candidate clock period +7% | -1.04453% | -1.02399% | -1.02521% |

Independent empirical q was **2.99466309** and **2.99044980** waves/active slice-cycle. All eight observed gains were within the preregistered 0.02 absolute-gain error tolerance; q errors were below 0.03. Local self-tests passed, including a deliberately wrong one-port-per-bank negative control. **Hosted result remains pending until the GitHub Actions job completes**; local validation is not hosted verification.

## Interpretation and falsifiers
The test confirms a *conditional accounting model on synthetic stationary traffic*, not a GPU speedup. In particular, a bandwidth- or port-saturated system gets no additional useful throughput from the optimistic extra slice, and only a 7% candidate clock regression erases the area-reinvestment opportunity. The result is a restatement of physical-resource conservation plus independently tested stochastic demand, **not a claim of novel GPU architecture theory**.

The latest paired critical-path diagnostic (run 40270157106) was still running at inspection. Both original integrated implementations fail the frozen 3.5 ns timing/electrical requirements, and the balanced-return detailed routes timed out. The only defensible next hardware step is measured critical-cone localization, followed by a matched RTL repair and complete extracted timing/hold/slew/cap/DRC comparison against an independently optimized equal-resource serial control. No RTX-5090 equivalence or power advantage is established.
