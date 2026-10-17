# V176 — SCIENCE ledger (2026-10-17)

**One active research kernel:** Does the V153 cutset's balanced mapped logic depth translate into a robust timing/area advantage once operand-arrival delay is charged to the V-Tile?

- **Frontier:** V156 matched OpenSTA (Nangate45, one lane, 10 ns, 0.05 ns input delay) gives V151 slack -2.93 ns, V153 +1.65 ns; V153 mapped area is 3.48% higher. V175 proves a necessary V153 setup failure for uniform arrival later than 1.70 ns, conditional on unchanged netlist/constraints. V173 actual seven-point sweep has NOT executed.
- **Exact objective:** Determine worst slack and critical-path class at input arrivals 0.05, 0.5, 1, 2, 3, 4, 5 ns; measure the first true crossover, if any. Separately check a 0.5 ns guardband at the 10 ns target.
- **Strongest resource-matched baseline:** V151 buffered reference with the same 2-cycle interface and same library; additionally require an optimized V151 variant with total mapped area no greater than V153. The latter comparison is PENDING, so no equal-total-area Pareto claim is allowed.
- **Mechanism hypothesis:** V153's cutset reduces maximum mapped combinational depth from 148 to 111 gates; both its input-to-register and register-to-register depth maxima are 111. Nevertheless, its input-to-register path can dominate because operand arrival is external to the pipeline. This predicts a sharp V153 10 ns setup feasibility boundary near 1.70 ns under the frozen model, not necessarily a V151/V153 crossover.
- **Decisive falsification:** A matched OpenSTA sweep or measured issue/RF arrival distribution that violates the predicted V153 feasibility envelope, or a resource-matched V151 implementation that beats V153 on realistic workload throughput and area/timing.
- **Publishable success threshold:** A previously unreported mechanism-derived timing/throughput law that survives equal-total-area control, multi-corner PPA, unseen workloads, independent checking, and a prior-art novelty audit. Current evidence does not meet this threshold.
- **Architecture-relevance threshold:** Demonstrated 10% improvement in a workload-weighted FP32 tile throughput/area-delay measure, with at least 0.5 ns 10 ns setup guardband and no functional regression. PENDING.
- **Kill/reformulate condition:** If three substantive discriminators neither improve the claim nor reveal a new timing boundary, pivot from fixed cutset retiming to operand-capture/arrival budgeting or equal-resource dense response credits. Do not stop Vektor.

## New structural evidence (exact, not timing)

From archived V156 mapped Verilog, a recursive gate-graph traversal and an independent iterative topological traversal agree at every flop D input. V151: 5,789 combinational cells, 162 flops, maximum gate depth 148 (register-origin). V153: 5,857 combinational cells, 195 flops, maximum gate depth 111 (both input-origin and register-origin). Depth decreases 25.0%; this is NOT a 25% timing improvement and is NOT scientific novelty. Source-class counts select one maximizing witness on ties.

## Evidence boundary

Original V156 netlists and STA reports are preserved in GitHub Actions run 38969084092 and the V175 evidence archive. SHA256 digests and derived counts are in evidence/structural_depth.json. V156 branch received the V176 Tcl and parser files, but attempts to publish an executable sweep runner and a dedicated workflow were blocked. No new STA sweep was performed. The old V156 infrastructure failure was resolved in commit 9122cbc3 and is not being reclassified as scientific falsification.

**Evidence class:** Exact structural graph calculation from archived synthesized netlists. No routed PPA, silicon, GPU equivalence, or novelty claim.
