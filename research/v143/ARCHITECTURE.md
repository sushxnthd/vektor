# V143 ARCHITECTURE — 2026-10-13

**Candidate block:** three-source Wave32 RF duplicate-read coalescer with physical bank arbitration downstream, preserving V142 producer-level writeback multicast. Requires stable source tags through RF responses; no integrated collector/scoreboard/FMA yet.

**Verified first CI run:** GitHub Actions 38381018667 PASS, 3456 independent abstract request/response cases, 800 full-Wave32 RTL test vectors. Yosys generic synth: 3-response-input coalescer 9286 generic cells (6144 muxes), longest topological path 12 cells. Passthrough 6 cells, path 1. **These are generic logic proxies, NOT mapped area, clock frequency, power or silicon.** Passthrough consumes more RF reads; not an equal-functionality system comparison.

**Architecture consequence:** blindly implementing 3x1024-bit response crossbar costs considerable generic logic. New alternative: single tagged 1024-bit RF response bus with valid-only qualification and data fanout by wiring. This changes response bandwidth (3 concurrent vectors to 1), so must be tested under serialization; NOT a free Pareto improvement.

**Model result:** strongest coalesced no-forward baseline removes forwarding wins in 2x-duplicate FMA family (0/32 holdout), but 1x and 3x families retain conditional wins. No equal-area/energy claim.

**5090 gates:** FP32 INCONCLUSIVE; tensor INCONCLUSIVE; graphics INCONCLUSIVE; ray INCONCLUSIVE; memory INCONCLUSIVE; cache/NoC INCONCLUSIVE; software INCONCLUSIVE; physical PPA INCONCLUSIVE; reproducibility PARTIAL (isolated RTL/model only).

**Next decisive experiment:** equal-resource response bus-width/serialization sweep with real FP32 collector integration and Yosys mapped/timing comparisons.
