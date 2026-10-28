# V297 optimized rotating-serial control: hardware-strength falsification (2026-10-29)

## Decision under test
V297 bounded bank-rescue is the sole provisional architecture mechanism on this branch. V287 and V296 remain retired. The 370.272 um^2 mapped rotating-serial control in the previous four-way comparison is **not** an adequate hardware-strength baseline: its variable-index greedy loop is structurally expensive. The previous comparison already disclosed this weakness. Do not interpret that area difference as an architectural benefit.

This experiment replaces only the **control implementation**, not its scheduling policy, with `rtl/v297_rotating_static_core.v`. It uses the same three request inputs, 16 banks, two reads per bank, two issue slots, three-phase round-robin priority and one-cycle phase advancement. Its combinational decision is three statically ordered mux trees sharing exactly three pair-compatibility predicates. No additional queue, register-file ports, lookahead, or issue slots are introduced. It is a strong *same-policy* comparator, not a second active mechanism.

## Exact behavioral proof obligation and checks
For each priority phase, the serial greedy control takes the first valid request and the first compatible successor. Static priority expansions are:

- phase 0 (0,1,2): p01, p02, single 0, p12, single 1, single 2;
- phase 1 (1,2,0): p12, p01, single 1, p02, single 2, single 0;
- phase 2 (2,0,1): p02, p12, single 2, p01, single 0, single 1.

Each `pij` is true only when **both** corresponding requests are valid and four operand reads fit within the two-read-per-bank constraint. This ordering is an exact symbolic expansion of the existing greedy loop, including the important case where the first selected request blocks both successors but the successors are compatible with each other. Greedy must still issue the first request only.

An independent Python implementation enumerates **192** phase × validity × arbitrary pair-compatibility combinations (3 × 8 × 8), including unrealizable compatibility combinations, and checks **120,000** seeded concrete bank vectors across 16-bank uniform, one-bank hotspot and two-bank stress regimes. Both checks passed locally with zero mismatches. The deliberately wrong fixed-phase control was detected. The existing independent Python-to-clocked-Verilog trace now also checks the new RTL against the same 17,832 rotating-serial expected grants; this last gate is **pending hosted CI** and must not be reported as passed before verification.

## Predeclared matched comparison and kill rule
The existing [matched physical preregistration](V297_MATCHED_PHYSICAL_KILL_PREREG_20261029.md) remains unchanged. Five mapped contestants now include original V297 (retired implementation), compact V297 (sole candidate implementation), original rotating serial (weak implementation), **optimized static rotating serial (strong same-policy control)**, and unrestricted max-pair (stronger scheduling control).

The mapped synthesis workflow now uses the same pinned Nangate45 library and ABC flow for all five. Its results are **mapped-cell-area and logic-depth proxies only**. Do not infer routed frequency, physical power or GPU performance. Next run must inspect the hosted mapping and then run matched placement/CTS/routing, electrical checks and extracted-RC STA at frozen 3.5 ns, +50 ps setup guard and 2x wire RC.

At the previously measured synthetic iid workload, V297's advantage over rotating serial was only +1.009%. It therefore loses the same-workload throughput comparison if its clock frequency is below approximately **99.001%** of the rotating control's clock (assuming equal per-cycle completion and no other bottleneck). On the frozen bursty regime, V297 was already worse at equal clock. If optimized rotating serial or unrestricted max-pair is physically feasible and matches/exceeds V297's throughput with no worse resource cost, **retire V297**. Do not introduce a new mechanism during this gate.

## Evidence limitations
- Independent symbolic and concrete checks: PASS locally.
- New clocked Verilog and pinned five-way mapped synthesis: configured, hosted result not yet confirmed.
- Matched routed area, STA, hold, max-cap/max-slew, DRC, power: **not measured**.
- Workload-level GPU throughput and tile-level consequence: **not measured**.
- Bank-aware scheduling and maximum-compatible-pair selection have substantial prior art; no novelty claim is made.
- Kernellum PR #119, its prospective holdouts and all other Vektor branches remain untouched.
