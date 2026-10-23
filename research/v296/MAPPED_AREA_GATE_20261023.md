# V296 mapped-area gate — 2026-10-23

Source: GitHub Actions run 39891959178, job 120213562905, artifact 12475740775 (SHA256 d47efe27b6b695de173ce7a1a6423fac0f7b6381f837dbbdde07dc40ae688931). Source revision: 2c283497bff8ffe6786bf20c9f934baa5f795770.

Three-way differential RTL simulation: PASS. Synthesis: Yosys 0.33, ABC Nangate45 typical Liberty; same V-Tile 4 issue slots, 16 RF banks, 2 read ports/bank. Reported mapped standard-cell area:

| Variant | Cell area (um^2) | Relative to best control |
| --- | ---: | ---: |
| Original V-Tile | 4046.126 | 1.07037 |
| Optimized one-hot decode-after-select | 3780.126 | 1.00000 |
| V296 pairwise | 3098.368 | **0.819647** |

Area reduction versus strongest control: **18.0353%**, or 681.758 um^2. This is a meaningful *positive mapped-area result*, **not yet** a physically validated architecture win. The combinational arbitration fanout and comparator chain may worsen arrival time, slew, capacitance, and wire delay. Area estimates exclude placement and routing. No STA or power results exist; frozen workload holdouts remain sealed.

**Decision:** V296 survives the first characterized *cell-area* gate only. Next gate is matched constrained OpenSTA on saved mapped netlists with input/output delay, realistic loads, max transition/capacitance and wire sensitivity. If timing and equal-resource efficiency do not survive, retire. No V-Tile integration or 5090-equivalence claim.

Reproduce: .github/workflows/v296.yml, research/v296/compare_area.py; original raw logs and netlist inputs are in the linked CI run.