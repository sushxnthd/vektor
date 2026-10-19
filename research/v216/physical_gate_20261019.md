# V216 physical gate (2026-10-19)
- Baseline: shared-predecode, 128 scoreboard entries, 4 groups, 8-bit tags.
- Candidate: same control plus group-local AND isolation of the tag.
- GitHub Actions run 39180258169: 10,000-vector differential RTL simulation PASS.
- Yosys generic synthesis: control 2,326 cells; isolated 2,358 cells (+32, +1.376%).
- Matched Liberty mapping/STA: NOT DONE. Sky130 Liberty URL returned HTTP 404.
- Physical conclusion: no demonstrated Pareto improvement; structural toggle model alone cannot qualify the mechanism.
- Architectural consequence: no integration; no FP32 V153/V156 revival.
- Next physical attempt must use a verified Liberty URL; if mapped timing/energy cannot substantiate a benefit, retire.
