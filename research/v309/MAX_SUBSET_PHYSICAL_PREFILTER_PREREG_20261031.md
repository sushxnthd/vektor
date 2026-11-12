# V309: prospective maximum-subset bank-admission physical prefilter (2026-10-31)

**Evidence tier: protocol only.** This is a *single exploratory successor* to the retired V296 admission-equivalent arbitration, on the existing V309 research branch and draft PR #26. No hardware mechanism is promoted by this document. V287 remains retired. The accepted QV100 Pathfinder/LUD bus-width null is a separate simulator result and is not used to select favorable workloads here.

## Question and prior-art boundary

V296 and optimized serial one-hot implement the same priority-greedy admission function, so their matched-clock issue-throughput ratio is identically one. A previously independently checked *mathematical* maximum-cardinality subset oracle in V296 showed a small synthetic opportunity under bank conflict, but **it was not hardware**. Maximum subset selection and bank-aware scheduling are established optimization concepts; do not claim novelty for exact enumeration.

Can a **synthesizable, combinational, four-slot maximum-cardinality admission controller** exploit the demonstrated policy headroom while retaining the exact resource contract and a defensible control-area/timing budget? This is an intentionally harsh early physicality prefilter. It must be compared with the existing serial-greedy bank arbiter on **identical** 4 request-valid bits, eight 4-bit bank addresses, 16 banks and two read ports per bank. Both issue at most four waves/cycle. A same-bank two-source request consumes **two** ports, never one.

## Frozen functionality and tie-break

Enumerate all 16 request subsets, reject invalid requests and any subset requiring >2 reads from a bank, then maximize number of granted requests. On ties, choose the **numerically smallest four-bit grant mask** (a deterministic tie-break, not fairness). The incumbent is `vektor_rf_bank_arbiter`. A separate testbench oracle must derive bank demand from explicit per-bank counts, not call either RTL implementation.

## Frozen test cases before evaluation

- **Predicted win motif**: all four requests valid; ordered operand banks (0,1), (0,0), (1,1), (2,2). Greedy grants 0 and 3 (mask 0x9, 2 issues); optimal grants 1,2,3 (mask 0xe, 3 issues). Required exact functional delta = +1 issue.
- **Predicted no-win motif**: all four valid; ordered pairs (0,1), (2,3), (4,5), (6,7). Both grant 0xf, exact delta = 0.
- **Exhaustive reduced-bank equivalence**: all 16 validity masks and all 3^8 operand-bank assignments, 104,976 input vectors, compared to an independent exact subset oracle; assert per-bank read-port safety and `popcount(optimal)>=popcount(greedy)`.
- **Out-of-domain controls**: bank IDs 0..15, invalid requests, duplicate operands, and a deliberate wrong-count mutant; no claim of complete 2^36-input formal proof unless separately performed.

## Physicality prefilter and hard stop

Run source-controlled Icarus RTL simulation and Yosys generic synthesis on the same hosted toolchain for the candidate and incumbent. Report generic cell count and combinational logic-depth proxy if available. These are **not** standard-cell area, extracted RC, frequency or power. Predeclare a coarse **candidate cell-count ceiling of 2.0x** the serial-greedy baseline at the same synthesis script. Exceeding this ceiling kills the **current brute-force RTL implementation** before expensive physical work, even if the functional win motif passes. Failing simulation or any resource-contract violation also kills it. A passing prefilter only authorizes later matched standard-cell synthesis, setup/hold/cap/slew/DRC, wiring/load sensitivity and workload-level validation; it does not establish a GPU win.

The stronger real-hardware comparison must include an optimized greedy serial controller and a low-overhead bounded-lookahead alternative, matched ports, clock, area and scheduling latency. The exact-max policy may starve older requests; fairness/liveness, scoreboard correctness, timing feedback, occupancy, compiler mapping and real workloads are **not** proved here.

## Evidence handling

Commit protocol before RTL outcomes. Preserve all failures and complete logs. No force push, merge, new research branch, GPU performance extrapolation, or RTX 5090-equivalence claim. Kernellum PR #119 remains separate.
