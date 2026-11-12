# V312 factored RTL functional and generic synthesis result (2026-10-31)

Source-pinned [GitHub Actions #41181927525](https://github.com/sushxnthd/vektor/actions/runs/41181927525) passed both independent jobs. The same 50,002-vector bank-port oracle accepted the original counted implementation and the new one-hot factored implementation, including same-bank two-read cases, frozen hotspot and disjoint vectors. The independent numerical audit passed five mutation controls; occupancy/bandwidth sensitivity script ran successfully.

| Same-mechanism RTL encoding | Yosys 0.33 generic mapped cells |
|---|---:|
| Variable-indexed two-bit per-bank counters | 3,422 |
| One-hot used-once/used-twice factoring | **1,625** |
| Relative change | **-52.51%** |

This is a meaningful **implementation-size reduction**, not a new architecture mechanism. It uses the same inputs, outputs, issue slots, bank count, read ports and grant policy. The counted implementation is a matched functional implementation control, **not** a strong alternative scheduling policy. No clock, mapped standard-cell area, electrical or real-workload result follows from the generic cell count.

The factored implementation is the preferred exploratory encoding for subsequent matched Nangate45/OpenROAD testing, subject to stronger architectural controls. Before physical promotion, compare against a competent bank-aware two-choice scheduler and an operand-collector-decoupled baseline; read [prior-art/collector challenge](PRIOR_ART_OPERAND_COLLECTOR_CHALLENGE_20261031.md).

**Do not claim a GPU speedup, novelty, or RTX-5090 equivalence.**
