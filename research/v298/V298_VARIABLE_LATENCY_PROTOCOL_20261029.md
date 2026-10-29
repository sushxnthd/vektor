# V298 variable-latency and false-dependency prospective test (2026-10-29)

## Pre-result freeze
This protocol and `v298_variable_latency_falsification.py` are committed to the existing V298 branch **before** executing `--evaluate`. Unit selftests (not holdout outputs) may be run before freezing. Synthetic finite-MSHR model only; no GPU IPC, routed PPA, or novelty claim.

Hypothesis: a one-bit dependent-credit guard protects the final MSHR after a critical return until the dependent request is ready. Stronger implementable one-bit comparator `phase_reserve` protects the final MSHR throughout a scoreboard-visible critical chain. Work-conserving critical-first and fixed one-credit reserve are additional controls. All policies have four MSHRs, one admission/cycle, identical exogenous arrival sequences, preassigned request-indexed memory service times, and critical-first issue. Background service times are uniformly distributed within frozen integer ranges; critical service times are uniformly 6..10 cycles. Predicted dependent miss can be false negative on intermediate critical returns or false positive on final return. False positives cancel after a fixed known delay; indefinite noncancellation remains a separate demonstrated liveness failure.

Four holdout seeds 503, 509, 521, 523, 40,000 cycles each. Parameters: background service interval, background arrival probability, interburst gap, critical chain length, compute delay, false positive probability, false negative probability, cancellation delay.

- V1 long stable (32..32, .30, 240, 8, 4, 0, 0, 4): predicted conditional guard win vs work-conserving; phase-reserve may dominate latency at greater background cost.
- V2 variable long (8..64, .30, 240, 8, 4, .15, .10, 8): predicted reduced or unstable guard advantage; stronger one-bit phase reserve is primary control.
- V3 short no-win (4..12, .50, 240, 8, 4, 0, 0, 4): predicted no material guard advantage vs work-conserving.
- V4 false-positive (8..64, .30, 240, 8, 4, .85, .10, 48): predicted background harm from false guard holds, potentially defeating phase reserve on joint objectives.
- V5 long cancel (16..48, .30, 240, 8, 4, .50, .05, 96): predicted false-positive background harm.
- V6 low traffic (8..64, .025, 240, 8, 4, .15, .10, 8): predicted no material guard advantage.

**Primary conditional gate:** V1 must improve mean critical burst latency >=10% versus work-conserving while retaining >=90% of its background completions and >=110% of fixed-reserve background completions. **Equal-state survival gate:** in at least one of V1/V2, guard must improve mean critical burst latency >=5% versus phase-reserve **or** retain >=10% more background completions at no more than 5% worse mean critical burst latency. Otherwise guard's distinct advantage over a strong one-bit control is not established. **Robustness gate:** V4/V5 must retain >=90% work-conserving background completions, or false-positive sensitivity is a serious practical failure. No tuning after holdout observation. Report per-seed and means; preserve all failures.

The isolated-credit identity `max(0,Lb-D)` is not asserted as a multi-MSHR predictive law. For random Lb, the candidate one-credit delay law is E[max(0,Lb-D)], conditional on final-credit collision; collision probability, critical-path sensitivity, cancellation delay, predictor precision and bandwidth determine realized benefit. No general positive law is established by this test alone.

Next gate if survives: implement equal-state phase-reserve RTL with independent equivalence and matched Nangate45 mapped/extracted-RC physical test; otherwise retire V298 or narrow it explicitly. Preserve existing PR #15, never merge automatically. Kernellum untouched.
