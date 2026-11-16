# Research Activity

Updated: 2026-11-17 (UTC)

- Active research branch: `research/v317-sass-provenance-gate`
- Active draft PR: #34
- Latest durable research commit: `4c7870cc65c982cd03b01b42c60c51d23ded3bd1`
- Evidence: added and fetched a strict-order two-request, one-port-per-bank combinational RTL reference control with explicit assertion harness. The control forbids deeper lookahead overtaking; it is not a new V296 mechanism or a physically validated GPU implementation. RTL simulation, synthesis, routing, extracted-RC electrical legality and GPU workload throughput remain unverified. Ledger is visibility only, not validation.

---


- Active research branch: `research/v317-sass-provenance-gate`
- Active draft PR: #34
- Latest durable research commit: `a384c51b9564479d59ba4b0b01e1824455f3f126`
- Evidence: committed and fetched an independently executed bounded-lookahead bank-queue competitor falsifier. Synthetic exhaustive binary sequences of lengths 2–10 reveal adjacent-only pairing can lose to four-entry lookahead at identical bank-port count; lookahead is NOT proven equal-area or electrically viable. No repaired routing, extracted-RC legality, DRC or measured GPU throughput. This checkpoint is visibility only, not validation.

---

Updated: 2026-11-12 (UTC)

- Active research branch: `research/v317-sass-provenance-gate`
- Active draft PR: #34
- Latest durable research commit: `2ca31cfadfb3be6409c70b4a903102b15a08aa72`
- Evidence: committed a prospective exact-rational interval clock/workload falsification gate. Under explicitly hypothetical ranges, uniform 16-bank traffic is rejected even by an optimistic oracle; hot-bank traffic remains conditional, not validated. Source presence was verified; script execution, repaired detailed routing, extracted-RC legality, DRC and measured throughput are not established. Prior matched area/electrical failures remain binding. This ledger is visibility only, not release approval.

---

Updated: 2026-11-11 (UTC)

- Active research branch: `research/v317-sass-provenance-gate`
- Active draft PR: #34
- Latest durable research commit: `32cb8f2febac95e14970ac440e2a6698888af988`
- Evidence: added a separate exact exhaustive small-bank falsifier for four-slot two-source/two-port compact greedy versus a maximum-cardinality oracle, including rational arithmetic, grant-delta distribution, and a self-test. This is new independent checker code, not a completed physical experiment or measured GPU throughput. Routed electrical violations, the compact-baseline area falsification, and missing verified DRC remain binding. Checker execution on hosted CI is not yet established.
- Prior V296 throughput no-go and V317 physical failures remain binding. Ledger is visibility only, not release approval.

--- 

Updated: 2026-11-10 (UTC)

- Active research branch: `research/v317-sass-provenance-gate`
- Active draft PR: #34
- Latest durable research commit: `a948fcad2c755fd9d0d955e9a446e2033b7ed10f`
- Evidence: the prospective repair acceptance checker previously documented a same-run requirement without enforcing it. Added experiment identity checks for paired routes and workload service, rejection of missing/mismatched provenance, and regression assertions. This is a fail-closed falsification of the prior checker, not new routed timing or measured GPU throughput. Existing electrical violations and absent verified DRC signoff remain binding.
- Prior V317 physical/electrical failures and V296 throughput no-go remain binding. This ledger is visibility only, not release or validation approval.
