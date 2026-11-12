# V309: independently source-attested published cycle-repeatability result (2026-10-30)

**HOSTED PASS:** [GitHub Actions #41064052478](https://github.com/sushxnthd/vektor/actions/runs/41064052478) at commit `73d37bf38850ee66834fed77042e3aa7a02afbdf`, [raw JSON artifact #12981471987](https://github.com/sushxnthd/vektor/actions/runs/41064052478/artifacts/12981471987). The [frozen protocol](PUBLISHED_CYCLE_REPEATABILITY_PROTOCOL_20261030.md) at `df69f2b` preceded executable implementation `73a151a`.

## Result from independent published Accel-Sim cycle evidence

Two externally authored public issue comments were fetched by **exact comment ID**, parsed independently, and verified against a frozen ten-workload table with full workload paths, not family-only names.

| Publicly reported simulator configuration | Repeats per workload | Rodinia 2.0-ft workloads | Workloads with nonzero reported cycle range | Largest within-workload relative range |
|---|---:|---:|---:|---:|
| QV100-SASS (2022-12-21 comment) | 4 | 10 | **0/10** | **0%** |
| RTX2060 (2023-03-28 comment) | 2 | 10 | **9/10** | **2.0130%** |

The largest RTX2060 relative range is **783/38,897 = 2.0130087%**, from the SRAD-v2 row (39,680 versus 38,897 reported cycles). BFS alone had identical two-run values. Both frozen predicted regimes passed.

The published tables originate in [Accel-Sim issue #60](https://github.com/accel-sim/accel-sim-framework/issues/60), specifically [comment #1361450799](https://github.com/accel-sim/accel-sim-framework/issues/60#issuecomment-1361450799) and [comment #1486100160](https://github.com/accel-sim/accel-sim-framework/issues/60#issuecomment-1486100160). The first author reports an Accel-Sim release commit `2260456` and GPGPU-Sim commit `13c6711` in the QV100 experiment; the RTX2060 report explicitly uses a different CUDA/trace version. These are **third-party published simulations**, not newly run by Vektor, not hardware measurements, and not demonstrated to share the exact Tesla V100 trace digest of the V309 archive.

## Independent controls

- Source attestation retrieved both original comment bodies through GitHub's public API and required exact agreement on all ten complete workload keys and their 4/2 cycle values.
- Offline parser fixtures passed, including two changed-value mutants and two duplicate-row mutants that must fail closed.
- Workload-key conservation and strictly positive cycle values passed.
- The report explicitly refuses to infer V309 physical speedup from any descriptive cross-configuration ratio.

## Architecture qualification consequence

A single trace-driven simulator run is not a sufficient precision gate for a small claimed improvement. For any future V309 hardware mechanism, preregister repeated identical-config runs, report per-workload cycle distributions, and compare an equal-resource baseline under identical trace, simulator revision, compiler settings, memory config, scheduling assumptions, and seeds. **A claim within the repeatability/noise envelope is not a demonstrated speedup.** The 2.013% figure is a historical configuration-specific observation, **not** a universal error bar or hardware-noise estimate. Four identical QV100 runs do not prove all future runs deterministic.

**No-go:** The QV100/RTX2060 tables cannot be joined to V309's source-conditional sector counts to estimate cycles or memory traffic because the run identity, architecture config, trace revision, simulator revision and hardware-counter provenance are not matched. The large V309 interleaving sensitivity remains unresolved.

**Next decisive experiment:** A version-pinned, authenticated Accel-Sim trace-driven run of a small V309 Rodinia 2.0-ft kernel, repeated under one QV100-SASS configuration with exact simulator and GPGPU-Sim SHAs, recording simulated cycles, cache/memory counters, occupancy/stalls, and source identity. The matched-resource architecture comparison must then proceed through RTL, synthesis, electrical and routed timing. This public-data audit does not substitute for it.

No hardware mechanism promoted. V287/V296 remain retired; V309 qualification branch and draft PR remain the sole active workstream. No physical GPU speedup, power result, or RTX 5090 equivalence is claimed. Kernellum PR #119 remains unchanged.
