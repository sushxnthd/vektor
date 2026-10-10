# Vektor-089 — Frozen preregistration, 2026-10-10

**Classification:** DISCRIMINATION and CAPABILITY-BUILDING; boundary-cycle reclamation is an EXPLOITATION follow-up. Parent Vektor-088. Models are synthetic.

**P1:** For two-bit wrapping generation tags, cancellation followed by immediate reuse can falsely accept an old completion within a bounded six-cycle callback horizon. **P2:** Quarantining each tag until after its issue_cycle+D prevents false acceptance under callback latency <=D but introduces stalls. **P3:** If callbacks arrive after D, quarantine may fail. **P4:** Enlarging the tag pool reduces stalls in the tested single-live-slot workload but finite traces need not show monotonically increasing useful throughput.

**Controls:** identical offered input streams; immediate wrap, conservative quarantine, unique-ID oracle; bits 1,2,3,4; D 3,6,9; cancellation probability 0,0.25,0.6; seeds 100..111; 2,000 cycles each. Add 54 minimally theory-guided surprise configurations (11.11% of 486 total; the initial planning note estimated 12.5%, corrected here). Count false accepts, correct completions, admissions, tag stalls. Test deliberate bound violations separately.

**Follow-up B, frozen before execution:** callback-first ordering permits tag reclamation at t>=issue+D instead of t>issue+D. Predict zero false accepts under bounded callbacks, fewer stalls, and a sufficient no-stall threshold of N>=D tags for at most one admission/cycle. Sweep D=2..16 and N=2,4,8,16,32 under continuous cancellation, plus randomized schedules. Counterexample to generality: if callbacks can arrive after admission in their nominal due cycle, the optimization requires a different ordering contract.

**Evidence standard:** compare against independently coded C++ event model and bounded exhaustive action traces; no GPU-level or silicon claims. Cheapest next discriminating experiment: implement synthesizable cancelable token allocator, verify with RTL and bounded formal tools.
