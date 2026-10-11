# Vektor-099 — FINAL/cancel race contract audit

Date: 2026-10-11. Class: DISCRIMINATION + CAPABILITY-BUILDING.
Baseline: V094 consumer from V097 branch. V098 composed RTL remains unverified.

## Frozen prediction and outcome

If cancellation must win over same-cycle FINAL, V094 emits an incorrect
completion when pending, live, cb_valid, cb_final, cancel_mask[tag] are all 1
and soft_reset is 0. A cancellation-masked match changes this classification
to stale_drop without changing tag retirement. All other Boolean combinations
should agree.

Local Python oracle enumerated 64 combinations: V094 1 cancel-wins violation,
V099 0; exactly 1 policy difference. Independent C++ oracle replicated all
counts. Residual against prediction: zero. These are combinational software
results, not sequential RTL formal verification. CI RTL and generic synthesis
are to be recorded separately; no physical timing/area/power measurements.

## Mechanism and adversarial interpretation

V094 evaluates cb_live_match from pre-edge live state before applying
cancel_mask. This implements FINAL-wins, which is coherent if intentionally
specified. It is a counterexample only under the cancel-wins contract.
V099 implements cancel-wins for pre-edge tag incarnation. Neither design
protects against duplicate FINAL callbacks or proves external flush_ack.
Unbounded fairness, hardware timing and GPU-level performance remain untested.

World model: KNOWN=V094 FINAL-wins; BELIEVED=cancel-wins preferable for
externally observable cancellation; CONFLICTING=both are coherent contracts;
FALSIFIED=V094 implements cancel-wins; ANOMALOUS=none in truth table;
UNTESTED=sequential RTL equivalence, multi-producer composition, PPA.

Explorer: explicitly encode cancellation priority. Skeptic: not a universal
bug. Experimentalist: one tag, one simultaneous FINAL and cancel.
Analyst: report both policies. Anomaly Hunter: investigate tag reuse boundary.
Prior-Art Auditor: priority logic is established practice, not novelty.
Replicator: independent C++ truth table. Theorist: classification depends on
linearization order, not on FIFO capacity.

Single next decisive action: run GitHub Actions RTL tests and generic synthesis,
then integrate the chosen contract with V098 multi-producer composition and
bounded sequential verification. RTX 5090-class gate: INCONCLUSIVE.
Personal spend: $0.
