# Frozen V317 rotating-priority equal-port RTL control (2026-11-01)

This is a **strong simple control** for the rejected maximum-cardinality selector, not a new active GPU architecture mechanism. Keep existing research branch and draft PR #34. Frozen before implementing/synthesizing the rotating-priority RTL. Earlier posthoc four-bank streaming results motivated this test and are NOT prospective evidence.

## Identical service semantics

Four request slots; 16 banks; each granted instruction consumes exactly two physical register-file reads (same-bank operands consume two ports). Two read ports per bank, no sharing, no extra ports, no extra issue slots. Rotate the starting priority slot each cycle, including idle cycles. Compare with source RTL `rtl/vtile/rf_bank_arbiter.sv` and previously committed exact challenger.

The new implementation may use a 2-bit phase register, bank-input permutation, original greedy arbiter, and inverse output permutation. Count **all** phase, mux, and arbiter logic. The fixed-priority reference does not need a phase register; this cost difference is real.

## Frozen hypotheses and tests

1. Functional: for each phase in 0..3, all 4,096 two-bank 4-slot combinations (16 validity masks x 4^4 operand encodings), the rotating RTL equals an independent priority-ordered oracle. Check all 16-bank directed cases, same-bank two-read capacity, reset and wraparound.
2. Physical: the rotating control is predicted to be smaller and shallower than the exact maximum-cardinality RTL. This is a **prediction**, not an observed result. Measure matched generic Yosys cell counts, longest combinational path and fanout; if the prediction fails, preserve the failure. The source-pinned exact comparator from run 41275143656 has 5,116 generic cells and 72 logic levels; fixed priority has 1,321 cells and 49 levels.
3. Workload: previously seen p=.60 four-bank overload (seed 317260) showed rotation near age-aware throughput, but is posthoc. Freeze an **unseen** stable four-bank p=.52 seed 317952 (predicted no material throughput gain, <1%), and an **unseen** stressed p=.60 seed 317960 (predicted rotation avoids unbounded backlog relative to fixed priority over 30,000 cycles, but may match oldest-first). Evaluate exactly once after implementation. Compare fixed, rotating, oldest-first and age-aware exact on identical arrivals.
4. Negative control: private banks p=.55 seed 317955, predicted zero completed-work improvement.
5. No-win rule: a rotating scheduler is not novel if the same throughput/tail gains are available to a simple age-based policy, or if physical cost negates them. A generic-cell advantage over exact is insufficient for GPU IPC. No promotion without standard-cell timing, wire/load, tile area, power, representative workloads and a predictive regime boundary.

## Evidence limits

Generic Yosys is not electrical closure. A four-slot synthetic FIFO service simulator is not a GPU. Never report speedups over a weak fixed-priority comparator as novel if rotating or oldest-first controls achieve them. V317 forwarding and exact maximum-cardinality selector remain no-go.
