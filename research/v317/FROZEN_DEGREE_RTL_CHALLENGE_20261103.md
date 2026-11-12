# V317: frozen degree-controller RTL adversarial challenge (2026-11-03)

## Scope and non-promotion
This is a **strong simple-control challenger** for the already-falsified V317 exact/area narrative, not a replacement active architecture mechanism. Preserve draft PR #34 and its existing branch. No V287 reset, no GPU IPC claim. All historical physical and electrical failures remain binding.

## Frozen question
Can the inexpensive oldest-request-preserving conflict-degree policy be expressed in synthesizable four-slot RTL with the **same 16 banks, two independently charged operands per request and two read ports per bank**, and how much logic overhead does it incur against the previously strongest V309 compact greedy implementation?

## Mechanism and controls
- All valid requests are candidates. Head (slot 0) is mandatory when valid.
- Compute each candidate's static degree as the count of *other valid candidates* sharing at least one bank, including self-bank operands as two physical reads.
- Visit slots 1..3 in ascending degree, stable slot-ID tie break; grant only when total demand at every bank stays <=2. Slot 0 is visited first.
- Compare with unchanged V309 compact greedy RTL and a separately implemented exact head-preserving software oracle.
- Degree sorting is not assumed optimal. No additional bank ports, no operand sharing or bypass.
- Use the exact same compact greedy arbiter after a permutation; the new sorting logic is included in synthesized area.

## Frozen verification before RTL results
1. Exhaustive 2-bank, four-slot operand combinations and all 16 valid masks: 4,096 cases. Compare RTL with independently calculated greedy degree reference, enforce legality, head inclusion and conservation.
2. Exhaustive 3-bank combinations and all valid masks: 104,976 cases in Python independent checker. Explicitly count degree wins and losses versus compact greedy and exact head.
3. Synthesis with identical generic Yosys settings for compact greedy and degree challenger. Report cells; no claim of matched physical area from generic cells.
4. Two frozen witnesses: degree win [valid=1110; (0,0),(0,1),(0,0),(1,1)] and degree loss [valid=1111; (0,1),(0,2),(1,2),(2,2)]. In both, preserve bank-port legality.
5. No threshold tuning after results. An electrical/timing claim requires matched OpenROAD routes, identical clock, loads, die and library, zero setup/hold/cap/slew/fanout/DRC violations.

## Kill gates
Any RTL mismatch or overgrant kills the implementation. If degree adds material logic/timing overhead without sustained throughput advantage over compact greedy, reject as a hardware mechanism. Even a valid generic synthesis and a combinational gain do **not** qualify as GPU throughput or an integrated tile result.

## Independence
The Python exhaustive checker must not import the RTL model or reuse the RTL's degree-sort code. Save exact raw counts and counterexamples, including negative cases.
