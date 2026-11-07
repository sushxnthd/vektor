# V317 prospective adversarial uniform-wire capacitance boundary: source-pinned result (2026-11-01)

## Reproducibility and evidence tier
**PASSED**: [GitHub Actions run #41328695515](https://github.com/sushxnthd/vektor/actions/runs/41328695515) at exact head `d9fa86f5ff2993a524e0139641fc9695406f723f`. The frozen protocol was separately committed first at `c55f100`, before the new checker, tests or synthesis. The same pinned Nangate45 typical Liberty (`git hash-object=90e4afb274cfc6514c587c434c77903d554117d1`) and unchanged fixed-priority RTL were synthesized by matched Yosys/ABC. The run passed **19 unit tests**, the two matched syntheses and all seven frozen prospective assertions. [Raw 8-file artifact #13091764983](https://github.com/sushxnthd/vektor/actions/runs/41328695515/artifacts/13091764983) preserves mapped netlists, logs, source SHA, Liberty and the complete machine-readable sweep.

**This is an adversarial analytical capacitance stress test on mapped cells, not actual placement, routed parasitic extraction, a physical timing result or GPU throughput.** The frozen thresholds were derived from earlier zero-wire measurements and therefore constitute a checker-transfer test, not novel independent empirical prediction.

## Matched mapped-cell results
Both use the same BUF_X1 output stage at 24 fF. Each characterized mapped output driver receives an equal additional `c` fF of hypothetical wire capacitance. Primary-input driving `grant[0]` remains uncharacterized.

| Extra wire capacitance **per mapped output net** | Original bank-mask violations / 731 nets | Pairwise bank-credit violations / 200 nets |
|---:|---:|---:|
| 0 fF | 0 | 0 |
| 0.5 fF | 0 | 0 |
| **1.0 fF, frozen predicted win** | **1** | **0** |
| 2.0 fF | 1 | 0 |
| **4.0 fF, frozen predicted no-win** | **2** | **1** |

Exact maximum additional **uniform per-net** wire capacitance that leaves all characterized internal outputs legal:

| Matched core | Minimum ideal-wire cap margin | Uniform-wire robustness threshold | Worst driver |
|---|---:|---:|---|
| Original bank-mask | 0.680998 fF | **0.680998 fF** | NOR4_X1, `_0837_`, net `_0049_` |
| Pairwise bank-credit | 3.838028 fF | **3.838028 fF** | NOR4_X1, `_244_`, net `_092_` |

The pairwise threshold is **5.6359x** the original's, under the deliberately equal-per-net wire-capacitance adversary. The result is conditional, not a measurement of wire lengths or capacitance after layout.

For intuition only, if each wire had exactly **0.1 fF/um**, the corresponding worst-net length ceilings would be 6.810 vs 38.380 um. At **0.2 fF/um**, the ceilings would be 3.405 vs 19.190 um. These are hypothetical conversion factors, **not characterized Nangate45 routing-layer RC values**. Neither comparison can establish which design actually routes better, since placement, fanout geometry, layer selection, coupling and buffering are absent.

## Independent controls and falsification
- Both mapped cores pass at zero extra wire, matching the previous independent max-cap audit.
- The source's first internal failure occurs at 1 fF; the pairwise core has no characterized internal violation at 1 or 2 fF.
- **Both fail at 4 fF.** This explicitly kills any claim that pairwise is unconditionally electrically admissible.
- The checker rejects negative, nonfinite and empty inputs, checks exact-boundary behavior and preserves the direct-primary-input caveat.
- There is no change in grant decisions, register-file ports or intrinsic scheduling throughput: **1.000x at equal clock/resources**.

## Physicality ladder: next required gate
A real matched place-and-route run must preserve the same mapped RTL and cell library, place both under identical utilization/IO constraints, insert characterized input/output driving stages, extract actual per-net wire R/C, and report max-capacitance, max-transition, setup/hold, wire length, buffers, mapped/routed area and power proxies. Test at least one plausible low-load regime and one high-wire-load regime without changing the predictions after results. An integrated tile-level critical-path and bandwidth model is required before any throughput claim. If routed timing/area or bandwidth erases an advantage, record the negative result and reject the GPU-speedup claim.

**Research decision:** retain pairwise bank-credit as a potentially more wire-cap-tolerant implementation optimization under this adversarial envelope; do not promote it as a novel GPU scheduling mechanism, routed signoff or RTX-5090-equivalent architecture.

Reproduce: `python3 -m unittest research.v317.rtl.test_rf_wire_cap_envelope research.v317.rtl.test_audit_rf_max_cap -v` and the pinned workflow `.github/workflows/v317-rf-wire-cap-envelope.yml`. Kernellum PR #119 was not modified.
