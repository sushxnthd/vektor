# V317 banked RF-proxy frozen physical gate: FAIL (2026-11-02)

## Provenance and method

- Frozen protocol: `research/v317/FROZEN_BANKED_RF_PROXY_TILE_GATE_20261102.md`, committed before implementation.
- Frozen RTL/physical source: `fb76565c9319266bd3efa285b435130f06150bf2`.
- GitHub Actions run: https://github.com/sushxnthd/vektor/actions/runs/41417132386 (job passed).
- Original raw 233-file ZIP: https://github.com/sushxnthd/vektor/actions/runs/41417132386/artifacts/13128827361 ; SHA-256 `8dd35d7a7f07c6939795975dabd3dc38c596b6a00c6fbda5163e374f054c7e8f`.
- Pinned OpenROAD-flow-scripts image: `openroad/orfs@sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8`.
- Independent audit: read the original ZIP directly, assert provenance, RTL 4,096-cycle pass, ABC area mapping, extracted-RC reports, route status, final DRC, all timing/electrical metrics, 1,213 sequential cells and zero macros. The existing repository checker is `research/v317/rtl/audit_rf_proxy_banked_tile.py`. Audit was performed separately from the GitHub Actions routing job.

## Frozen matched result

Both variants use the identical 16-bank, two-read-port, flop-mapped RF proxy, four 8-bit words/bank, registered operand sink, Nangate45 library, 3.000-ns clock, 240 x 240-um die, same physical constraints and synthesis settings.

| Extracted-RC metric | Source | Pairwise |
|---|---:|---:|
| RTL 4,096-cycle equivalence | PASS | PASS |
| Route process exit | 0 | 0 |
| Routed standard-cell area (um^2) | 21,610.6 | 21,432.2 |
| Sequential cells | 1,213 | 1,213 |
| SRAM macros | 0 | 0 |
| Fmax (MHz, reported controller proxy) | 390.763 | 448.080 |
| Setup slack (ps) | +440.907 | +768.257 |
| Setup violations | 0 | 0 |
| Hold slack (ps) | **-1.57355** | **-0.400319** |
| Hold violations | **3** | **4** |
| Max-capacitance violations | **11** | **8** |
| Max-slew / max-fanout violations | 0 / 0 | 0 / 0 |
| Final detailed-route DRC | 0 | 0 |
| Wire length (um) | 284,662 | 287,232 |
| Default-activity power proxy (mW) | 10.6252 | 10.5349 |

The pairwise implementation saves **178.4 um^2**, or **0.825521%** of the matched RF-proxy-controller area. This is **below the prospectively frozen >=2.0% criterion**, and **neither implementation is electrically legal** because hold and capacitance violations remain. The physical gate therefore fails independently on two criteria.

A zero route exit and zero final DRC do not establish electrical signoff. Positive setup slack also does not erase negative hold slack or maximum-capacitance violations. The 14.668% controller-proxy Fmax ratio is not an integrated GPU clock or throughput measurement. Pairwise wire length is 0.903% **higher**, and the default-activity power-proxy reduction is only 0.850%, not a calibrated power result.

## Quantitative falsification and boundary

At the measured source area, the preregistered 2% whole-proxy area threshold would require pairwise area <= **21,178.388 um^2**. The observed pairwise area exceeds this by **253.812 um^2**. This is not an uncertainty interval; it is a deterministic shortfall at this frozen configuration.

The matched grant/operand-equivalent designs have **1.000x intrinsic same-clock service throughput**. The previously conditional 25-versus-24 tile packing argument cannot be transferred to this RF-proxy result. No positive GPU throughput result survives this gate.

## Decision

**FROZEN GATE FAIL. Kill the V317 RF-proxy-integrated positive GPU-performance interpretation at this configuration.** Preserve the negative result; do not silently relax the 2% threshold or call the route electrically clean. The pairwise bank-credit design remains only a bounded controller implementation observation, not a validated architectural throughput mechanism. Do not revive historical V287 or start a second mechanism.

Next scientifically meaningful work, if retaining the single V317 physical workstream, is a *separately preregistered* matched electrical repair (hold/cap) and stronger legal source challenger, followed by real SRAM-macro/datapath tile P&R. It must not retroactively change this FAIL. A novel positive boundary law and unseen GPU workload validation remain missing.

**Evidence tier:** flop-mapped banked RF proxy, **not** an SRAM macro, real GPU tile, silicon power measurement, GPU IPC, or RTX 5090 equivalence.
