# V309 follow-up: exact operand-service identifiability counterexample

Date: 2026-10-30. **Exploratory synthetic trace-format fixtures; not externally captured SASS, not GPU cycles.** The V309 qualification PR remains the sole active workstream. No hardware candidate is promoted.

## Claim tested
Can static PTX register-source counts (or even a multiset of physical source-register identities) identify operand collector bank-service demand without per-instruction source pairing, collector capacity and bank mapping?

**No.** Two independent, two-source instruction sequences use exactly the same source-register multiset `{R0,R1,R2,R3}`, identical instruction count, opcode, active mask and output destination. Under `bank = register_id mod 2`, one read port per bank and one collector, grouping `(R0,R2); (R1,R3)` takes four RF-service cycles, while `(R0,R1); (R2,R3)` takes two. The 2x difference persists despite the same aggregate bank totals (two reads per bank) and the same static operand count. This is a counterexample to identifying bank-service cycles from aggregate source counts alone, **not** an assertion that a GPU executes either trace this way.

## Exact finite-collector sweep

| Banks | Ports/bank | Collectors | Grouped cycles | Crossed cycles | Ratio |
|---:|---:|---:|---:|---:|---:|
| 2 | 1 | 1 | 4 | 2 | 2.00x |
| 2 | 1 | 2 | 2 | 2 | 1.00x |
| 2 | 2 | 1 | 2 | 2 | 1.00x |
| 2 | 2 | 2 | 1 | 1 | 1.00x |
| 4 | 1 | 1 | 2 | 2 | 1.00x |
| 4 | 1 | 2 | 1 | 1 | 1.00x |
| 4 | 2 | 1 | 2 | 2 | 1.00x |
| 4 | 2 | 2 | 1 | 1 | 1.00x |

An exact dynamic-programming oracle minimizes cycles under finite collector admission and bank-port budgets. Two analytical extremes cross-check it: with one collector, `T = sum_i max_b ceil(d[i,b]/P)`; with at least as many collectors as instructions, `T = max_b ceil(sum_i d[i,b]/P)`. The second equality assumes no dependencies, dispatch overhead or execution latency. Exhaustive verification covers 1,536 two-instruction assignments across 2/3/4 banks and 1/2 ports, plus seven parser fail-closed mutants. The simulator also applies free intra-instruction duplicate-source broadcast.

## Scientific interpretation and kill criterion

The **2x apparent benefit disappears** when either a second collector is available, the port budget doubles, or the bank mapping spreads the four registers over four banks. Therefore, any purported Vektor bank-scheduling improvement derived solely from PTX source counts is non-identifiable without hardware-grounded collector occupancy, physical SASS register mapping, port service, dependencies and memory behavior. No architecture is justified by these synthetic counterexamples.

This result does **not** show that a real GPU has one or two collectors, any particular register-bank mapping, or a twofold scheduling opportunity. No physical timing/area, power or throughput claim follows. The two frozen 2026-10-29 PTX sources target different GPU generations and remain unsuitable for hardware-matched throughput claims. This experiment is not a prospective holdout and has no novelty claim beyond a constructive identifiability demonstration.

## Reproduce

`python3 research/v309/sass_identifiability.py --selftest`

The parser accepts a documented *subset* of Accel-Sim plaintext instruction rows and intentionally refuses memory payloads. Its generated fixtures are **not** real Accel-Sim captured traces. Source format reference: https://github.com/PSAL-POSTECH/accel-sim-tracer . The current Accel-Sim 2.0 framework uses compressed `.tracez` files that require its traceDsm decoder: https://github.com/accel-sim/accel-sim-framework .

## Next physical evidence gate

Acquire at least one authenticated dynamic SASS trace with paired hardware counters, then three independent families for mechanism qualification. Verify register-identity semantics, mask widths, collector assumptions and bank mapping against the relevant GPU generation. Pre-register win/no-win workload regimes before using a trace for a candidate. Keep V287/V296 and all failed mechanisms retired absent new physical evidence. Kernellum PR #119 remains untouched.
