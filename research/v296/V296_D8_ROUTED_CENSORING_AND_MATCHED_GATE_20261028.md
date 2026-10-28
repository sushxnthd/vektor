# V296 deferred-write D8 routed censoring and matched-feasibility boundary (2026-10-28)

**Decision:** The D8 V296 contestant completes the detailed-route extracted-RC metrics and clears the frozen physical guards, but the D8 optimized serial comparator times out after 75 minutes. The matched D8 outcome is therefore **censored**, not a V296 win and not a verified serial physical failure. D4 has two complete measurements but the serial comparator violates setup and hold. There is **no depth with two feasible matched routed contestants**. The D4 preregistered WIN prediction is falsified; the D8 preregistered NO_WIN prediction remains unverified due to missing control measurements.

## Immutable provenance and evidence tier

Source: [GitHub Actions run 40646515864](https://github.com/sushxnthd/vektor/actions/runs/40646515864), frozen head SHA `84245c21f485c191aea7d352652c0ef036d6d047`. Original job logs: D4 pairwise 122676592244, D4 serial 122676592295, D8 pairwise 122676592311, D8 serial 122676592217. Original artifacts: 12800301495, 12800782354, 12803073531, 12804941948. The independent aggregate jobs 122731739548 and 122731739526 both returned fail-closed incomplete verdicts. This report transcribes original contestant log metrics; it is **not** an independent artifact re-extraction, silicon signoff, or a power/performance measurement.

Frozen physical guards: setup slack >= +50 ps, hold slack >= 0 ps, zero reported max-cap/max-slew violations, integrated area <= 30,000 um². Identical depth and physical flow required for comparisons.

| Depth / contestant | Routed area (um²) | Extracted setup (ps) | Extracted hold (ps) | Cap/slew | Outcome |
|---|---:|---:|---:|---|---|
| D4 V296 | 19543.020 | +66.661 | +10.758 | 0/0 | Pass |
| D4 optimized serial | 21914.943 | -323.617 | -11.207 | 0/0 | Fail |
| D8 V296 | 26723.956 | +59.643 | +11.642 | 0/0 | Pass |
| D8 optimized serial | **unavailable** | **unavailable** | **unavailable** | **unavailable** | **Timeout (exit 124)** |

## Physicality law: feasibility must precede architectural comparison

For architecture a at depth d define
`F(a,d) = complete(a,d) AND area<=Amax AND setup>=50ps AND hold>=0 AND cap_viol=0 AND slew_viol=0`.
A matched routed comparison is eligible only if `F(V296,d) AND F(serial,d)`. The pairwise win gate further requires an occupancy-adjusted throughput advantage at equal resources and physically justified frequency. This prevents two common errors: (i) treating a control's timeout as proof that the candidate is faster, and (ii) treating the infeasible control's measured area as an eligible matched Pareto baseline.

For the D8 candidate, setup headroom beyond the guard is **9.643 ps** and hold headroom is **11.642 ps**. For D4 V296 the corresponding margins are **16.661 ps** and **10.758 ps**. D4 serial requires at least **373.617 ps setup recovery** to reach +50 ps and **11.207 ps hold recovery** to reach zero, before considering changes in paths, RC, area or clock. These are lower bounds under the measured fixed implementation, not a feasible repair.

At the frozen 30,000 um² integrated ceiling, each *completed* contestant fits only **one** routed slice. The D8 serial integer count cannot be inferred. A V296 integer packing benefit is not demonstrated. The retiming adds one operand latency cycle; previous occupancy break-even calculations must be applied to any subsequently demonstrated clock change. There is no demonstrated same-resource GPU speedup, power saving, or RTX-5090 equivalence.

## Reproducibility and falsification

Run `python3 research/v296/v296_matched_censor_gate.py --self-test`. It reproduces the numeric guard arithmetic with Decimal, exhaustively checks 16 completion/exit combinations for fail-closed behavior, and outputs a machine-readable audit. It intentionally does not fabricate missing D8 serial measurements. Original artifact ZIP integrity and source-provenance checks remain the responsibility of the existing independent routed checker.

**Next experiment:** preserve the existing V296 mechanism, branch and PR. Diagnose which D8 serial stage timed out from its preserved log/artifact, then perform a bounded, symmetric same-depth timing/hold repair with unchanged RF ports, depth, clock and flow. Require both complete physical passes before workload-level matched claims. A timeout-only retry without a substantive physical change is not a scientific advance. Keep D4 WIN falsification and D8 censored outcome in the ledger; do not reopen V287.
