# V189 — Equal-storage collector RTL discriminator

## Active architectural question
Does V188's sticky operand storage preserve V187's coalesced issue/dispatch behavior and improve payload activity without violating equal-storage timing and area constraints?

## Frontier
V187 predicts 0.333 issues/cycle for three distinct operands with two RF responses/cycle in an ideal model; V188 reports exact software-model payload transition savings but neither variant has passed an executed RTL miter or synthesized equal-resource PPA gate. V151 is still FP32 integration reference. V156 matched OpenSTA is green after an infrastructure repair, but the seven-point arrival sweep is unexecuted.

## Objective and strongest baseline
Execute a directed plus randomized SystemVerilog equivalence test of V187 vs V188 with identical RF responses, writebacks, stalls and tags, and synthesize both under identical Wave32 parameters. V187 is the equal-storage baseline (3,072 operand payload bits).

## Mechanism and quantitative prediction
V188 replaces clear-to-zero/refill with retain/overwrite. In the register-transition model, avoided bit toggles equal 2*popcount(old & new) per fully overwritten word, without changing issue timing. The prediction fails if invalid retained values leak into valid dispatch, if a response is lost, or if physical overhead outweighs the benefit.

## Decisive falsification
Any divergent accepted/retired tag or valid payload, any missed same-cycle dispatch/enqueue, any liveness violation under fair RF and downstream service, or matched synthesis/timing overhead that negates usefulness.

## Publishable success threshold
Novelty beyond standard operand retention, frozen realistic kernels, matched physical PPA and equal-budget baselines, independent checker, predicted crossover, unseen traces, and >=5% repeatable performance/energy improvement. NOT MET.

## Architecture threshold
Executed RTL PASS, same 3072 payload bits, no throughput regression, <=5% tile area overhead, and realistic workload benefit. NOT MET.

## Kill condition
If RTL or PPA fails, preserve counterexample and pivot to collector-limited throughput with a valid equal-budget control. If three runs add no boundary or claim, reformulate the kernel.

## SCIENCE
Elementary transition identity and synthetic model only; no scientific novelty established.

## ARCHITECTURE
Candidate collector control/payload implementation; no physical signoff or tile integration yet.

## Evidence class
Modelled; pending RTL/synthesis.

## Pending gates
V187/V188 RTL miter, Wave32 Yosys area/timing proxy, RF bank-conflict trace, V156 seven-point OpenSTA sweep.
