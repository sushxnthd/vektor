# V296 integrated tile-slice routed physical falsification (2026-10-28)

**Decision: integrated physical gate FAIL.** This result is distinct from the earlier D4/D8 deferred-write micro-slice experiment. It is not legitimate to combine its area or timing with that different implementation or to claim a tile-level benefit.

## Original evidence

[GitHub Actions run 40675850164](https://github.com/sushxnthd/vektor/actions/runs/40675850164), workflow source commit `21505ad2541d5be6135ed84fc33697146cf75b8e` (checkout merge `a928da6`). Both physical jobs completed and uploaded artifacts; independent aggregate job 122842515393 **failed closed with exit code 3**. Original artifacts: pairwise 12814114032 (ZIP SHA-256 e1fc2beaffd856c7a4ee45f27a249de019357115b2b5682b12fa4d7b6b51092a); serial 12819900185 (ZIP SHA-256 5831ffef5fa3de5e2b863088459f0dbafff1f87ca51b5bcbeb3ab9dac4e52240); aggregate 12818818436 (ZIP SHA-256 64a09ad4cd63dba6b741aa6f6d53896ac7a7cf0eb31d0e32bbfc6bb4b7d9e92f). These are original Actions log/artifact metadata, not independent downloaded artifact re-extraction.

| Integrated extracted-RC metric | V296 pairwise | Strong serial one-hot |
|---|---:|---:|
| Final area (um2) | 17857.644252 | 18953.830505 |
| Setup slack (ns) | **-1.047895** | **-1.859922** |
| Hold slack (ns) | **-0.036622** | **-0.019796** |
| Max-cap violations | **3** | **3** |
| Max-slew violations | 0 | 0 |
| Complete physical gate | **FAIL** | **FAIL** |

The independent aggregate reported a 5.78345% candidate area saving and +0.812027 ns candidate setup lead, **but both architectures violate setup, hold, and cap**. A lead against an infeasible control is not a matched physically feasible win. The frozen integrated guard here is **+0.250 ns setup**, not the +0.050 ns guard in the separate deferred-write D4/D8 experiment. The 30,000 um2 ceiling is met by both but does not rescue timing/electrical failure.

## Necessary repair envelope, not a proposed successful fix

At the measured fixed implementations, candidate setup must improve by at least **1.297895 ns**, serial by at least **2.109922 ns** to reach +0.250 ns. Candidate hold needs at least **36.622 ps**, serial **19.796 ps**, and both must eliminate three max-cap violations. These are arithmetic lower bounds, not achievable repairs. Critical paths can migrate and parasitics can change; timing fixes can worsen area, hold, and cap. Serial and pairwise repairs must be symmetric in resource constraints.

This integrated result is stronger negative evidence than a mere route timeout: both contestants completed and the independent checker returned an explicit physical fail. The existing D4/D8 deferred-write result remains separate: candidate passes at D4/D8, serial D4 fails and serial D8 was censored in that experiment. Do not combine those outcomes.

## Consequence for V296

**Reject the integrated-tile physical-win hypothesis for this configuration.** Do not count its 5.78% area saving as a demonstrated architectural or energy gain. At equal clock and latency, previously established exact admission equivalence also rules out an arbitration-only throughput advantage. The only scientifically admissible next step is a *predeclared, bounded upstream critical-cone repair* with unchanged 16-bank/two-read-port/four-slot resource contract and symmetric strongest-serial control. Require both designs to pass full routed extracted-RC setup, hold, cap/slew, DRC, then measured workload and energy before any claim. If the bounded repair cannot recover >1.3 ns candidate setup and electrical closure without breaking area/occupancy, **retire V296**, preserving this negative result. No new architecture mechanism is authorized by this report.

The counterfactual 40,000 um2 tile-packing sensitivity experiment in this branch uses **different D4 deferred-write areas**; it does not overturn this physical falsification. All real GPU workload holdouts remain sealed. Kernellum PR #119 is untouched. No RTX-5090 equivalence, physical power, or GPU speedup is claimed.
