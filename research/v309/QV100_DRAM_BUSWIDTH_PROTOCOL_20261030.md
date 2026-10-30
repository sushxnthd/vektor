# V309 prospective QV100 DRAM bus-width sensitivity gate (2026-10-30)

## Identity and frozen interventions
This is a simulator **bottleneck falsification**, not a GPU mechanism, speedup or matched-resource comparison. Preserve the original SHA-256-authenticated Rodinia 2.0-ft Pathfinder 1000_20_5 trace (four launches, two HtoD copies), source-pinned Accel-Sim/GPGPU-Sim QV100-SASS simulator, and unchanged baseline `-gpgpu_dram_buswidth 16`. Change **only** this active option to 8 and 32 bytes, with exact source and variant SHA-256 checks. All other options, including `-dram_latency 100`, must be byte-identical. Two complete replays per setting; independent per-kernel counters and strict completion markers are mandatory.

## Frozen predictions and kill tests
Prediction P1 (bus-service pressure): reducing modeled bus width 16 -> 8 will increase total simulated cycles. P2 (monotone service): raising modeled width 16 -> 32 will not increase total simulated cycles. Failure of either rejects the respective monotonic-bus-service hypothesis on this workload. Prediction P3 (small-win regime): increasing width to 32 yields <2% cycle improvement; >=2% rejects the small-benefit hypothesis. This is an **ex ante test**, not a retrospective fit. The 8-byte setting is the predicted adverse regime; the 32-byte setting is the predicted small-benefit regime. Neither is an architecture win/no-win *workload*.

Do not silently force cache counters to match: scheduler/interleaving may change with service timing. Require unchanged launches and instruction totals, record per-kernel L1/L2 and memory counters, and flag counter changes as a causal-attribution limitation. Reject missing, drifted, or duplicate active options and inconsistent repeats. If the simulator cannot complete a variant, record FAIL_CLOSED, not a result.

## Decision rule
If width effects are negligible, do not promote a DRAM bus-width optimization for Pathfinder. If material, require a second **unseen** workload and a matched-resource architectural alternative with RTL, synthesis, timing, electrical and power proxies before claiming a mechanism. Altering modeled bus width changes physical resources, so this test alone cannot demonstrate equal-resource advantage or an RTX 5090-class design. V296 and V287 remain retired. Kernellum PR #119 and its holdouts are untouched.
