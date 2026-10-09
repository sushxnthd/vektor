# Vektor-054 — Discovery Protocol V2 world model

**Date:** 2026-10-09. **Class:** CAPABILITY-BUILDING / DISCRIMINATION / EXPLOITATION. Evidence: Python reference, independent packed-state model, 24 Icarus RTL differential simulations, generic Yosys synthesis.

| State | Claim |
|---|---|
| KNOWN (software model) | 24 traces, 60,000 cycles, zero reference/replica disagreements; zero-alias controls exactly match. |
| KNOWN (RTL simulation) | 24/24 RTL differential tests passed in GitHub Actions run 37880347241; malformed response is detected. |
| KNOWN (generic synthesis) | DEDUP=1: 2323 generic cells; DEDUP=0: 2139; +8.60% overhead in this two-slot prototype, same 272 flip-flop cells. |
| BELIEVED | Tagged source dedup can reduce read demand under physical-register aliasing, but actual compiler alias rates are unknown. |
| CONFLICTING | Total reads drop 51% at 100% alias because more instructions complete; reads per completed instruction fall about 66.7%. Different denominators. |
| FALSIFIED | A 3x reduction in reads/instruction guarantees 3x throughput: 100%-alias modeled completions rise only 47.22%. |
| FALSIFIED | Same-instruction dedup/fanout has zero hardware-control cost: generic synthesis shows +184 cells. |
| ANOMALOUS | 25% alias yields only +5.77% modeled completions despite about 16.7% fewer reads per completion, indicating bottleneck migration. |
| UNTESTED | Technology-mapped area/timing/power, RF banks, real compiler traces, V-Tile/GPU performance, novelty. |

## Experiment 054A/B

Mechanism: two instruction slots, 3 source IDs, one request port, tagged out-of-order returns, duplicate read suppression, source-ID fanout. Equal-budget DEDUP=0 control. No bank arbitration, scoreboard or execution pipeline.

Predictions: zero-alias equality, fewer reads with alias, no cross-instruction operand mixing, malformed response rejected. Prediction document was finalized after local model grid and is not independently timestamped preregistration.

Outcome: 24 x 2500-cycle software reference/replica comparisons, 24 x 2500-cycle Icarus RTL differential simulations, 2 generic Yosys syntheses. All correctness tests pass; generic cells 2139 vs 2323 (+8.60% overhead). Baseline modeled completions 936 across three seeds; dedup 936/990/1089/1378 at 0/25/50/100% alias. All synthetic, not GPU IPC.

Residual: 0 RTL differential mismatches in 60,000 cycles; +184 generic cells. Uncertainty: 2 slots, synthetic alias rates, no bank ports, latency randomization, no physical PPA. Yosys flattened unpacked arrays to registers but reported 0 check errors.

Assumptions weakened: RF traffic reduction alone does not determine IPC; extra comparator/fanout logic is not free. Competing explanations for non-proportional gains: occupancy, return latency, completion backpressure and request-port bottleneck.

Adversarial roles: Explorer—tagged fanout; Skeptic—realistic traces and timing; Experimentalist—equal controls and invalid returns; Analyst—counts and limits; Anomaly Hunter—bottleneck migration; Prior-Art Auditor—GPGPU-Sim; Replicator—independent Python and RTL differential; Theorist—read bandwidth is only one ceiling.

**Foothold:** verified RTL correctness for this bounded two-slot contract and measured generic synthesis cost. Not a GPU-performance breakthrough. Prior negative branches from 047-053 retained. All RTX 5090-class gates INCONCLUSIVE.

**Single next action:** realistic compiler-derived alias traces and multi-slot, finite-bank PPA/IPC comparisons; technology-mapped timing before frequency claims.

CI: https://github.com/sushxnthd/vektor/actions/runs/37880347241
