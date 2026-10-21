# V263 frozen E0 — Last-missing-operand bank grant (2026-10-21)

Only active mechanism after V262 retirement. No V263 holdout has been evaluated.

Bottleneck: bank conflict can delay the final operand needed to issue a warp. Mechanism: prioritize scoreboard-confirmed last-missing operand, with age and starvation bound, without extra RF ports, queue slots or crossbar.

Law: recovered issue slots per cycle <= min(C*h*w*u, available idle slots), where C is contested grants, h is last-missing incidence, w is baseline wrong-grant probability, u is recoverable issue slots. Clock-adjusted win requires r*(I_base+Delta_I)/I_base > 1.

Controls: oldest-first with fairness; ready-first and optimized scoreboard-aware arbitration with identical metadata/ports/buffering; offline oracle as upper bound.

Frozen holdouts BEFORE source generation: positive seed 263101 (8192 grants, C>=.50, h>=.65, w>=.35, predicted >5% modeled IPC gain vs oldest-first at r>=.98); negative seed 263102 (C<=.04, h<=.05, <=1% gain); divergent seed 263103 (h<=.25, no robust win predicted). Freeze generator SHA before opening.

Gates: functional equivalence, RTL simulation, synthesis, electrical checks, matched timing/area, IPC/RF traffic, wire/load sensitivity. Retire if strongest equal-budget scoreboard control matches it, starvation appears, or PPA cost erases IPC gain. Prior-art risk high. Integrated tile unchanged. No RTX 5090 equivalence.
