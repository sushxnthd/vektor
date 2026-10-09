# Vektor-052 research ledger — 2026-10-09

Evidence: Python software reference only. RTL simulation and synthesis have NOT run.

## Experiment 052A — CAPABILITY-BUILDING
Mechanism: verify three register-read admission policies (clock RR, first-grant RR, completion-first) with independent selection logic and bank relabeling controls.

Prediction: 12,000 independently reproduced grant/count/pointer cases and 9,000 bank-relabeling checks should have zero disagreements for the fixed O=3, PORTS=2 contract.

Observed: 12,000 deterministic vector cases, 9,000 bank-relabeling checks, zero disagreements. Residual: zero. This verifies the vector oracle, not the SystemVerilog implementation. The RTL source and vector-driven testbench are committed separately.

Assumptions: pending and accepted masks are disjoint; 3 operands per wave; one outstanding instruction per wave; bank IDs in range; available slots are a per-cycle credit budget. Violating any assumption invalidates the result.

Competing explanations: both Python implementations could share the same policy misunderstanding; RTL behavior may differ; no real register data or response pipeline is modeled.

## World model
KNOWN: Python admission oracle cross-check passed in this bounded input model; Vektor-051 reported a queue-credit/hot-bank phase transition.
BELIEVED: completion-first requires more control hardware than first-grant.
CONFLICTING: conditional throughput recovery versus regressions and lower fairness than oldest-first in 051.
FALSIFIED: Vektor-051's 2L age-escape universal rescue; nominal bank count as a standalone contention proxy.
ANOMALOUS: 051 first-grant hot-bank throughput plateau.
UNTESTED: RTL differential, synthesis, physical PPA, tagged response collector, tensor/graphics/RT and RTX 5090-class capability.

## Next decisive experiment
Execute Icarus differential simulation for W/B = 3/1, 4/2, 8/4, 32/16 and POLICY = 0,1,2; then matched Yosys synthesis for 4/2 and 8/4. If CI cannot execute, do not report hardware validation.
