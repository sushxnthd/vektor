# V309 independent published cycle-repeatability gate (frozen 2026-10-30)

## Decision before inspecting outputs

This is a **negative control on simulator evidence reliability**, not a proposed GPU architecture or a new cycle model. It uses ten public `rodinia_2.0-ft` workload rows reported in comments on [Accel-Sim issue #60](https://github.com/accel-sim/accel-sim-framework/issues/60). The 2022-12-21 QV100-SASS four-repeat table is comment [#1361450799](https://github.com/accel-sim/accel-sim-framework/issues/60#issuecomment-1361450799). The 2023-03-28 RTX2060 two-repeat table is comment [#1486100160](https://github.com/accel-sim/accel-sim-framework/issues/60#issuecomment-1486100160).

The ten workload identifiers are exact table rows, not newly run by Vektor. Different GPU configurations, simulation revisions, CUDA/trace versions, and authors make cross-configuration cycle ratios **descriptive only**, not causal speedup or validation of V309's historical Tesla V100 trace digest.

### Frozen tests

1. **Predicted repeatable regime:** QV100-SASS: all ten workloads have zero reported cycle range across four repeats.
2. **Predicted nonrepeatable regime:** RTX2060: at least eight of ten workloads have nonzero reported cycle range across two repeats.
3. **No-go regime:** Any cycle model that joins either table to V309's 2020-03-18 Tesla V100 `rodinia_2.0-ft` archive without a byte-identical trace/run/config provenance key MUST refuse an architecture performance inference, even if workload names match.
4. **Independent source checker:** Fetch the two upstream comment bodies by numeric comment ID and require exact ten-key/value agreement with the frozen local table. Reject missing, duplicated, or changed rows; never silently adapt.
5. **Quantification:** Report exact max/min within-run ratios, symmetric relative variation and per-config range, plus descriptive cross-config ratios. Never call the latter matched comparisons. Include an adversarial changed-source rejection test.

### Stop rules

If public comments are unavailable, run offline arithmetic checks but label source attestation unverified. If comment tables changed, FAIL CLOSED. If any Vektor result would depend on treating different configs/traces as matched, kill that result. Even a passing gate provides **published third-party cycle evidence only**, not measured hardware cycles, calibrated V100 traffic, RTL timing, or GPU speedup.

No V287/V296 revival. Continue V309 qualification on its existing branch and draft PR.