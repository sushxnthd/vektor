# Vektor-082 preregistered predictions

Frozen 2026-10-10 before experiments. Class: DISCRIMINATION.

P1: Four-wide issue throughput cannot exceed four instructions/cycle even if operand-ready rate exceeds four.

P2: A single hot RF bank with two read ports limits two-source instructions to <=1 issue/cycle and four-source instructions to <=0.5.

P3: Bank-aware operand reordering improves at least one mixed-bank case; reversals are possible.

P4: With issue width >= collector count, fixed-order model reproduces Vektor-081 exactly.

P5: Adding collectors beyond the dominant resource limit cannot improve steady-state throughput.

Controls: identical instruction streams, collectors, RF bank budgets, and response latency. Matrix: 200 controlled configurations; 30 exploratory configurations (13.0%). Frozen holdout seeds 1701-1720. No physical implementation assumptions.
