# Vektor-059 — Discovery Protocol V2 world model (2026-10-09)

## Claim states

| State | Claim | Evidence / uncertainty |
|---|---|---|
| KNOWN | Tag-only return routing cannot distinguish multiple operand slots of the same instruction if returns reorder | Two-world indistinguishability counterexample; 3 operand responses require an operand index or equivalent sideband |
| KNOWN | A hypothetical globally merged 32 waves × 8 instructions × 3 operand responses requires at least 10 unique response-ID bits | 768 simultaneously active identities; 8-bit instruction-only IDs have 512 duplicates in the full-occupancy construction |
| KNOWN | Vektor-058 model's unique-tag assumption does not cover same-instruction multi-operand return aliasing | Audit of original oracle; newly constructed duplicate-tag stress model |
| BELIEVED | The 058 compacting queue is functionally correct under its stated handshake contract | 10,080 legacy and 216,000 new Python model-oracle comparisons, 43,200 independent C++ comparisons, all zero disagreements; not compiled RTL |
| CONFLICTING | The existing 8-bit RTL TAGW parameter can support a full Vektor-1A scoreboard | It is only a test width; cannot uniquely encode all 768 globally merged responses without sideband/channel identity |
| FALSIFIED | An instruction-only tag always suffices to route operands | Two-world counterexample |
| ANOMALOUS | 058's reference rejects duplicate tags even though queue RTL stores them | Reference contract is narrower than hardware interface |
| UNTESTED | Icarus simulation, formal temporal properties, Yosys PPA, integrated collector scoreboard, actual workload response multiplicity, epoch/replay lifetime | Free local HDL tools unavailable; no 059 CI workflow committed |

## Experiment 059-A — DISCRIMINATION

Mechanism: stable arbitration under arbitrary stalls and FIFO compaction. Prediction: zero model-oracle differences. Observed: 10,080 original + 216,000 new Python comparisons; 0 disagreements. Residual 0; does not validate RTL. Alternative explanation: both Python models share an assumption about age ordering. Cheapest discriminating experiment: Icarus RTL-vs-reference on 18 parameter configurations.

## Experiment 059-B — CAPABILITY-BUILDING

Mechanism: independent C++ transaction list oracle (max-age urgent, UID lock). Prediction: zero disagreements on 43,200 frozen vectors. Observed: zero. Residual 0; source-level independent but not a hardware proof. Cheapest test: execute Verilog vectors with Icarus.

## Experiment 059-C — DISCRIMINATION

Mechanism: operand identity ambiguity. Prediction: two distinct operand mappings yield identical instruction-tag-only return packets. Observed: yes, explicit two-world counterexample; 512 colliding operand identities at hypothetical 768 full occupancy. Residual 0. Weakened assumption: unique instruction tag implies unique operand response. Competing explanation: hidden operand index or channel-specific ordering, neither represented in the 058 interface. Cheapest test: add an operand-index field and route out-of-order returns into a reference scoreboard.

## Failure-cluster elevation

047–058 failures repeatedly involved arbitration phase, collector occupancy, backpressure, starvation and response scheduling. Vektor-059 elevates **response identity / scoreboard integration** as a separate correctness bottleneck. A queue can preserve data perfectly while a downstream consumer misroutes it.

## Architectural alternatives retained

- Explicit globally unique response IDs with allocation/free protocol (10+ bits under 32×8×3 bound).
- Per-wave instruction tag plus operand index; sideband wave ID retained by channel.
- In-order per-instruction operand returns with reduced metadata but higher head-of-line risk.
- Bank-local tag spaces with unambiguous bank provenance.
- Epoch tags with bounded stale-return lifetime; finite epochs alone do not guarantee safety under unbounded replay delay.

## Foothold and next action

A reproducible **structural correctness foothold**, not a throughput improvement or novelty claim. Next: run actual RTL differential/synthesis and implement a tagged scoreboard with operand-indexed response routing. 5090-class gate remains INCONCLUSIVE.
