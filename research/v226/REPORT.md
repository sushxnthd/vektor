# V226 — retired as a breakthrough candidate

Date: 2026-10-19. Positive model boundary: 100% modeled fetch-admission gain on coherent/two-PC-group synthetic holdouts; 0% on staggered-memory, divergent and distinct-ASID holdouts. This is not GPU IPC or energy.

Physicality: no RTL simulation, synthesis, electrical max-cap/slew, STA or power results. Same-budget PC-aware instruction buffering was not tested. Prior-art instruction fetch broadcast substantially overlaps the mechanism. No novel architecture law or Pareto improvement established. Do not integrate.

Frozen holdouts (baseline -> candidate cycles): coherent 346->173; two groups 334->167; memory staggered 1255->1255; divergent 298->298; distinct ASID 302->302. Python selector checker: 768 configurations passed. RTL/testbench/CI prepared locally but repository publication blocked by safety checks. The previous report commit is preserved in history.

Branch publication status: report only. Attempts to publish RTL and raw results failed; a dangling Git object is not a branch commit. Full local bundle: vektor226_fetch_multicast_retired_2026-10-19.zip. Next run must pivot to a different mechanism; V153/V156 FP32 timing claims remain retired.
