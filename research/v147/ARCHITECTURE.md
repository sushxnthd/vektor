# V147 ARCHITECTURE ledger

Built a software-executable Wave32 path: V146 collector contract -> bit-exact IEEE-754 FMA -> destination scoreboard -> three-cycle retirement/writeback, with two RF responses and divergent lane masks. This is software simulation, NOT a synthesizable integrated FP32 tile.

Decision: preserve flexible two-response routing and retain low-bit bank mapping as default. XOR indexing is a candidate for independent bank-concentrated operand traffic, showing 1.239x modeled holdout speedup but no gain on dependent bankhot at RF latency 1. Do not adopt without physical-cost and realistic-kernel tests.

Known blockers: one-instruction collector; no full Wave32 FP32 arithmetic RTL synthesis, frequency, area or power. V146 collector-specific HDL test is pending. All RTX 5090-class gates INCONCLUSIVE.

Next action: V146 RTL simulation and synthesis; then tagged Wave32 FMA writeback/scoreboard integration and matched mapped PPA.
