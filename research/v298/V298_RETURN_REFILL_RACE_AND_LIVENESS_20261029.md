# V298 same-cycle return/refill race and liveness audit (2026-10-29)

**Evidence tier:** RTL semantic counterexample plus independent executable reference; no physical timing, power or GPU IPC inference.

## Counterexample to the original macro

The finite-MSHR simulator processes a critical completion at time t, sets the dependent-credit guard, then arbitrates the returned credit at time t. The original clocked RTL instead used only registered `guard_q` to suppress background admission. With `guard_q=0`, `free_count=1` after the return, `critical_return=1`, `dependent_known=1`, `crit_ready=0`, and `bg_pending=1`, original RTL **issued background traffic using the credit the simulator had reserved**. The guard registered only at the next edge. This is a concrete functional mismatch, not a theoretical timing concern.

The repaired macro uses `effective_guard = !dependent_cancel && (guard_q || (critical_return && dependent_known))` for the same-cycle admission decision. Cancellation has precedence; the existing next-state logic remains unchanged. Both the guard and oracle policies now use this combinational condition. The clocked truth-table test checks all 2,560 policy/input/state combinations with the corrected independent expectation.

The separate `v298_return_refill_checker.py` enumerates the same 2,560 combinations with an independently structured reference, deliberately compares against the old equation as a negative control, and verifies the directed return/refill race. The original macro's earlier passing RTL test was therefore insufficient: it had encoded the same one-cycle-late assumption as the design.

## New physical burden and liveness contract

The correction introduces a `critical_return -> dependent_known -> background-admission` combinational control path. The original generic synthesis logs cannot establish its timing or area. The repaired path must be measured against the strongest implementable equal-resource controller under matched placement/routing/extracted RC and load variation.

A second independent counterexample holds `guard_q=1`, `free_count=1`, `bg_pending=1`, `crit_ready=0`, and neither `dependent_cancel` nor `crit_issue` for 256 cycles. The guard correctly blocks all background requests for all 256 cycles, but **cannot guarantee forward progress**. This is not an intrinsic deadlock of a full GPU; it is an interface contract failure if the scoreboard can leave a false dependent prediction uncleared. Either cancellation must be proved bounded, or a bounded timeout must be implemented and compared physically. No timeout has been added to the candidate.

## Scientific decision

Keep V298 provisional, not validated. The frozen H1/H2 synthetic holdout results are unchanged, but the former RTL evidence did not match their event ordering. Require hosted regression to pass on the repaired RTL, then test predictor false positives/cancellation delay and the new combinational path. Retire V298 if a strong equal-cost control dominates or physical cost erases the joint win. No new performance, energy, novelty or RTX-5090-equivalence claim is supported.
