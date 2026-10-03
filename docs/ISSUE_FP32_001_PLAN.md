# ISSUE-FP32-001

Goal: turn the scheduler/RF components into an integrated, backpressured V-Tile issue-control slice, then attach a standards-checked FP32 execution backend.

Immediate invariants:

1. A wave may advance scheduler fairness state only when the downstream RF admission stage accepts it.
2. Source-bank metadata is selected by issued wave ID, not pre-associated with scheduler slots.
3. RF conflicts may reduce issue width but must never drop or falsely retire work.
4. RTL tests must include accepted, partially blocked, fully blocked, and retry cases.
5. FP32 arithmetic is a separate evidence gate: IEEE-754 correctness and synthesis must be established before using arithmetic throughput in Vektor projections.

Current public reference baseline for the arithmetic stage: contemporary Vortex uses a fixed-latency pipelined FMA with unpack/classify, significand multiply, alignment, accumulate, normalize, and two-stage rounding. Vektor will use public/open implementations only as standards and PPA references; proprietary commercial RTL is out of scope.
