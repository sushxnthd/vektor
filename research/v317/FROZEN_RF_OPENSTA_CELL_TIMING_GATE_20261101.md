# Frozen V317 mapped-cell timing and electrical-load falsification (2026-11-01)

## Scope and provenance

Existing branch `research/v317-sass-provenance-gate`, draft PR #34. This is a physicality gate for the existing grant-equivalent pairwise bank-credit implementation, not a newly promoted architecture mechanism. Historical V287/V296 are not reopened. Baseline Nangate45 mapped-area run #41296883857, source SHA `0d62a15fd0c1046374f287a6c683333297e6139d`, and formal-equivalence run #41292817868.

## Predeclared experiment

Map four RTL variants using the same pinned Nangate45 typical Liberty, Yosys and ABC recipe: source fixed, pairwise fixed, source rotating, pairwise rotating. Export gate-level Verilog. Run OpenSTA on every netlist with the same 20-ps input transition and three output capacitive loads: **2 fF, 20 fF, 100 fF** (0.002/0.02/0.1 pF). Clocked rotating variants must include phase-register launch paths; fixed variants use a virtual clock. Use an explicit 10-ns reference period to avoid treating a passing reference clock as GPU frequency validation. Report worst grant-output data arrival, startpoint, endpoint, errors, mapped area and provenance. No missing or unconstrained path counts as success.

### Frozen directional predictions (not results)

1. **Implementation-area win:** pairwise fixed remains smaller than source fixed; pairwise rotating remains smaller than source rotating. This is already supported by mapped-area data, not a new holdout.
2. **Cell-delay win:** pairwise fixed is faster than source fixed at 2 and 20 fF; pairwise rotating is faster than source rotating at the same loads. The 100-fF load is a prospective stress test and may falsify either.
3. **Strong-baseline no-win:** optimized rotating is not presumed to beat optimized fixed on area, delay or service per tile area; its previous workload advantage was fairness-related and matched by oldest-first within ten completions. An identical grant policy has **1.0x intrinsic scheduling throughput** at equal clock and ports.

### Kill criteria and evidence tier

If any frozen cell-delay prediction fails at low/moderate load, retract the corresponding advantage immediately. Missing endpoints, unconstrained paths, missing tools or parser errors mean **unverified**, not pass. OpenSTA cell timing is **pre-route**: no extracted wire RC, placement, power, clock closure, GPU IPC or RTX 5090 equivalence. Preserve all raw logs, mapped netlists, source SHA and failures. Independent parser rejects missing paths, invalid arrival and errors. Routed timing and real register-file/tile integration remain mandatory.