# Frozen exact RF-bank issue selection physicality gate (2026-11-01)

Status: preregistered before writing a new exact-selection RTL comparator or inspecting its synthesis. This is a **challenger to the existing fixed-priority RF arbiter**, not promotion of the rejected V317 register-forwarding mechanism. Continue using draft PR #34 and its existing branch.

## Resource match and hypotheses

Both implementations receive the same four valid bits and two 4-bit source-bank indices per request. Every selected request consumes two independent physical bank reads, even if both indices are equal. Each bank has **two** read ports per cycle. No operand forwarding, identity reuse, extra bank port, extra issue slot, or clock-period relaxation is allowed.

* Predicted-win witness: valid=0b0111; pairs (0,0),(0,1),(0,1),(0,0). Fixed priority selects request 0; maximum-cardinality selection can select requests 1 and 2, so the predicted one-cycle issue-count ratio is 2.0.
* Predicted-no-win witness: valid=0b0011; pairs (0,0),(1,1),(0,0),(0,0). Both schedulers grant two requests, so ratio is 1.0.
* Exhaustively compare grant masks against an independently enumerated maximum-cardinality oracle for all 4096 two-bank configurations; separately check no bank exceeds two physical reads. The exact RTL must match deterministic highest-mask tie breaking. Test cases must include all-invalid, all-same-bank, mixed-bank and invalid-slot requests.
* Measure matched generic synthesis cells, logic depth and generic net fanout for the existing priority RTL and the exact-selection challenger, with identical Yosys commands. Run Icarus simulation for both. A testbench or synthesis failure is a failed gate, not evidence of success.
* Unseen transfer: use the already frozen fixed-seed four-bank 10,000-case workload in `rf_arbiter_port_audit.py`; do not retune on its results. Preserve the exact/greedy 16,606/16,428 optimistic grant-count ratio as a *synthetic, per-decision* ceiling, not IPC.

## Kill rule

If the exact-selection network materially increases generic logic cost or combinational depth, do not claim a practical improvement without equal-area/equal-clock physical timing closure, realistic arrival/critical-path checks, collector occupancy and workload queueing. Even if all RTL tests pass, no GPU throughput claim follows. If equal-resource matched physical timing or register-file traffic erases the gain, kill the scheduler as an architecture candidate. Existing V317 forwarding remains no-go.

## Limitations

Generic Yosys synthesis is not placed/routed timing, power, electrical signoff, or real GPU bank topology. Maximum-cardinality selection can penalize old requests and tail latency; these require explicit workload/fairness tests before any promotion. No RTX 5090 equivalence is implied.
