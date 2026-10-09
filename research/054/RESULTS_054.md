# Vektor-054B — RTL differential verification and generic synthesis evidence

**Run date:** 2026-10-09 UTC. **Commit under test:** `073b9682282a8f7caaa6a817fcdd23e62f494966`.
**CI:** https://github.com/sushxnthd/vektor/actions/runs/37880347241
**Artifact:** https://github.com/sushxnthd/vektor/actions/runs/37880347241/artifacts/11593903950
**Tools:** Icarus Verilog and Yosys installed from Ubuntu GitHub Actions apt packages. The exact tool version numbers were not captured; add version pinning next.

## Claim -> implementation -> experiment -> measurement

Claim: two-slot tagged collector suppresses duplicate same-instruction register reads without corrupting returned operands, and its hardware-control overhead can be bounded by a generic synthesis proxy.

Implementation: `rtl/rf_tagged_fanout_054.sv` with `DEDUP=0` vs `DEDUP=1`; both use the same tag/operand/return interface, two slots, 3 sources, 8-bit source IDs, 32-bit data, 8-bit tags. Independent Python transaction model generates vectors; separate packed-state Python implementation checks every expected cycle.

Experiment: 3 seeds x 4 alias levels x 2 policies x 2500 cycles = 24 RTL simulations, 60,000 total cycles. Every trace injects a malformed return. Zero-alias controls are exact. Equal-budget Yosys `read_verilog -sv; hierarchy -chparam DEDUP <0|1>; synth; stat` on the same source.

**Measured RTL verification:** 24/24 Icarus differential simulations PASS. **Measured generic synthesis:** Yosys `check` reports 0 problems for both configurations.

| Generic Yosys cell class | DEDUP=0 | DEDUP=1 | Delta |
|---|---:|---:|---:|
| Total generic cells | 2139 | 2323 | +184 (+8.60%) |
| Flip-flop cells (DFFE + DFF) | 272 | 272 | 0 |
| MUX cells | 1314 | 1314 | 0 |
| XOR + XNOR | 50 | 146 | +96 |
| Other generic logic | 503 | 591 | +88 |

These are **technology-independent generic cell counts, not mm2, transistor count, timing, or power**. The extra combinational cells suggest a real control-area cost to alias detection and fanout. Same flip-flop count is specific to this small prototype and not a full GPU RF.

**Software-model throughput:** three 2500-cycle seeds per alias level. Baseline completions 936 for all regimes; DEDUP completions 936/990/1089/1378 for 0/25/50/100% alias. Gains 0/+5.77/+16.35/+47.22%. This is a synthetic one-request-port/two-slot model, **not hardware IPC**. 100%-alias is an extreme artificial stress case.

**Residual and uncertainty:** RTL differential residual 0 in 60,000 cycles. Generic cell-count delta +184. No post-synthesis timing path, placement, clock, power, banked RF, scoreboard, compiler alias measurements, or GPU workload result. Model and RTL may share an architectural specification error. Yosys warns that unpacked arrays are flattened to registers; the synthesis completes with 0 check errors.

**Decisive next experiment:** measure realistic source alias rates from compiled open kernels, then scale the collector to 4/8/16 slots with finite bank ports and compare equal-budget PPA and workload IPC. Add technology-mapped timing before treating 2.56 GHz as plausible.

## Discovery Protocol V2 update

- KNOWN (RTL): 24/24 tagged return/fanout differential simulations pass, 60,000 cycles.
- KNOWN (generic synthesized): DEDUP=1 adds 8.60% generic cells relative to DEDUP=0 in this fixed two-slot block.
- BELIEVED: the added combinational logic can be justified in RF-constrained regimes; no real-kernel evidence yet.
- FALSIFIED: zero-cost alias fanout assumption; generic logic overhead is nonzero.
- ANOMALOUS: XOR/XNOR count rises 50 -> 146, consistent with equality-compare logic, but not independently proven to be the sole source of extra cells.
- UNTESTED: physical PPA, realistic alias rates, full V-Tile integration, GPU capability.
