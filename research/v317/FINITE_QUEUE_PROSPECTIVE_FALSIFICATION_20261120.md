# V317 finite-queue prospective stress (2026-11-20 UTC)

This is a **synthetic simulator**, not RTL, routed hardware, or GPU IPC. It evaluates the *same single V317 bank scheduler mechanism* against the strongest compact scan-greedy baseline with identical four-entry FIFO, four banks, two reads per request, and two bank ports. The protected maximum-cardinality competitor is an **unimplementable zero-cost upper-bound oracle**; the physical case is therefore weaker.

Protocol was fixed before execution: four independent seeds (20261121–20261124), 20,000 cycles each, first 2,000 excluded, arrival rates 1, 1.5, 2, 2.5 requests/cycle, and bank probabilities uniform, 65% hot, 85% hot. Deterministic paired arrivals are generated per seed/regime/rate. Admission is FIFO with drop-on-full; completed service occurs before arrivals. Requests always have two bank reads, including duplicate operands. Scheduler selections obey two ports per bank. No stateful fairness policy, physical overhead, wire/load, or energy is modeled.

## Observations (mean protected/greedy throughput over four paired seeds)

| Regime | 1.0 | 1.5 | 2.0 | 2.5 req/cycle |
|---|---:|---:|---:|---:|
| Uniform | 1.000000 | 1.000000 | 1.000028 | 1.004697 |
| 65%-hot | 1.000000 | 1.000030 | 1.000140 | 1.000426 |
| 85%-hot | 1.000000 | 1.000000 | 1.000000 | 1.000012 |

The **largest individual seed** observed was 1.004987 (uniform, 2.5 req/cycle). None of the 48 predeclared paired scenarios reaches the frozen 1.02 materiality threshold, even with a zero-cost protected oracle. This is an empirical falsification of the claim that the post-hoc hot-bank combinational stratum necessarily yields useful finite-queue throughput. It does not prove that all possible traffic patterns fail. The fixed simulator has a four-entry buffer and no GPU execution model.

## Reproduce and decision

Run `python3 research/v317/rtl/finite_queue_prospective_20261120.py > results.json`. Inspect the per-seed throughput, drop fraction and wait times in the JSON output. The script embeds the fixed prospective protocol and can be independently reimplemented. **Decision: NO-GO for promoting the protected oracle to physical design on these workloads.** Retain compact greedy as baseline; do not claim a 2% gain, RTX-5090 equivalence, or physical legality. Prior V317 compact-greedy area dominance and electrical violations remain binding. Any future alternative must first establish a meaningful finite-buffer gain with an implementable age-bounded controller and independent checker, then pass matched RTL/synthesis/route/electrical and wire/load sensitivity gates.
