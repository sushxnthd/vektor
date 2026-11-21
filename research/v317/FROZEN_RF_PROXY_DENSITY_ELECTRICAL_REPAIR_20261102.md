# V317 prospective matched RF-proxy electrical-repair challenge (2026-11-02)

## Status and lineage
This protocol is committed **before** the new physical routes and results. It continues the sole V317 pairwise bank-credit implementation on `research/v317-sass-provenance-gate` and draft PR #34. It **does not supersede** the frozen 2026-11-02 RF-proxy FAIL: 0.825521% area saving against a >=2.0% criterion, 3/4 hold and 11/8 max-cap violations. The older V287 dual-warp fusion is not revived.

## Question
Can a legally tuned **matched** placement-density setting repair hold and maximum-capacitance violations for both the original source and pairwise controller, and does the pairwise version retain a material whole-proxy area advantage? The source controller is the strongest equal-resource control. Neither design changes grants, register storage, bank ports, datapath, or clock.

## Fixed resources and constraints
- Exactly the existing `vektor_v317_rf_proxy_top_source` and `vektor_v317_rf_proxy_top_pairwise` RTL; 16 banks x 4 words x 8 bits, 2 reads per bank, 1 global write, registered sink; no SRAM macro.
- Pinned `openroad/orfs@sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8`; Nangate45, ABC_AREA=1, 3.000 ns, 0.100 ns uncertainty, 10-fF load, 240 x 240 um die and 8..232 um core.
- Two **prospectively frozen** additional placement-density add-ons: 0.15 and 0.35. Run both source and pairwise at each setting (four independent full P&R routes); no variant-specific tuning, different constraints, selective reruns or changing the RTL. The original 0.05 experiment remains a historical comparator, not part of the new matched decision.
- Preserve full Yosys, placement, routing, extracted-RC, power-proxy, electrical reports, container digests and per-route status even on failure. Do not discard negative routes.

## Predictions and decision rules (locked before outcome)
1. **Functional control:** repeat 4096-cycle cycle-exact grant/operand equivalence and two-read-port legality; any mismatch or overflow kills the design.
2. **Electrical gate:** both source and pairwise must report zero setup/hold violations, zero max-cap/max-slew/max-fanout violations, nonnegative setup and hold slack, and zero detailed-route DRC. Any failed route or missing extracted-RC report is **FAIL**, not an inferred success.
3. **Prospective no-material-win prediction:** pairwise whole-proxy area saving remains **below 2.0%** at both 0.15 and 0.35. This is falsified if any electrically legal matched pair achieves >=2.0%; failed/illegal pairs are indeterminate for the legal-area comparison. Report raw percentage even when illegal.
4. **Material implementation win criterion:** a *new* legal matched pair must save >=2.0% whole-proxy routed standard-cell area. No retroactive relaxation of the original threshold. Any result is limited to a small flop RF proxy.
5. **Throughput no-win prediction:** both RTL implementations emit identical grants and operands at a matched clock, hence intrinsic issue throughput ratio is 1.000x. Any observed grant-based speedup signals non-equivalence, not architectural gain.
6. **Power/wire sensitivity:** report default-activity power proxy and routed wire length for each pair, without interpreting them as silicon energy or a characterized GPU datapath.

## Outcome interpretation
If density tuning repairs electrical violations but area stays <2.0%, retain only the narrow controller implementation observation and reject the RF-proxy material win. If both legal and >=2.0%, retain as a *new* implementation-level candidate, still requiring real SRAM, datapath and tile-level P&R and workload validation. If electrical failures persist, reject physical claims. No result from this challenge establishes GPU IPC, RTX 5090 equivalence, architectural novelty, or a positive throughput law.

## Reproduction
The new `.github/workflows/v317-rf-proxy-density-electrical-repair.yml` runs both densities and both variants in the same pinned environment and retains raw artifacts. The checker `research/v317/rtl/audit_rf_proxy_density_repair.py` reads extracted-RC metrics and applies this frozen decision.
