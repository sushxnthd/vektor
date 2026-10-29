# V301 bounded RTL physicality probe, 2026-10-29

## Research status
The frozen N1/N3 strong-control experiment already falsified a robust eight-way CAM advantage: equal-eight-entry set4 retained at least 95% of V301's synthetic completion rate. The bounded-backpressure sensitivity did not reverse that finding. This is one bounded hardware gate, **not** a new positive claim or a retuned holdout.

## Reproducible implementation
- `v301_scoreboard_rtl.v`: clocked four-lane, eight-entry completion accumulator with epoch-safe OR, oldest-first one-port retirement, ready/backpressure, and a `FULL_CAM` parameter selecting eight-way CAM or two-set/four-way admission.
- `v301_rtl_oracle.py`: independent Python record-list cycle oracle; deterministic 1,024-cycle stress vectors per policy and per-(warp,epoch) bit-conservation assertion.
- `tb_v301_rtl.v`: cycle-accurate Icarus check of ready bits, output valid, warp, epoch and OR mask.
- `.github/workflows/v301-pilot.yml`: existing active CI extended to run Icarus and matched pinned Nangate45 Yosys synthesis. Liberty revision: `eda8e552974d47a12616294dddf4012d892548d3`. Separate `v301-rtl-gate.yml` also preserves a generic synthesis gate.

Local independent Python microtests and vector-generation conservation **passed** for both policies (1,024 cycles each). Hosted Icarus/Yosys outcomes are **pending**; no RTL pass, mapped area, timing or electrical result is claimed until logs are inspected.

## Fairness and evidence boundaries
1. The set4 variant is a **functional**, unoptimized control: it uses the same compacted queue and scans eight slots. It is **not** a physically partitioned, area-optimized four-way controller. A CAM win against this baseline would not establish equal-silicon superiority.
2. Rejected test-vector events are not retried; the RTL test is admission/interface equivalence, not a lossless end-to-end GPU workload model. The earlier bounded source model is the separate throughput evidence tier.
3. The single scoreboard write port is a hypothesis, not a verified limitation of contemporary GPUs. Epoch aliases on 8-bit wrap must be prohibited upstream.
4. Mapped Nangate45 cell area is **not** routed area, extracted-RC timing, DRC, hold, cap/slew, power or tile-level throughput. No RTX-5090-equivalence claim is supported.
5. If an optimized set4 or realistic two-bank implementation is no worse at matched routed timing and area while preserving its frozen >=95% throughput, V301 must be retired. Do not retune the opened N1/N3 workload motifs.

## Local reproduction

```sh
python3 research/v301/v301_rtl_oracle.py
for variant in 0 1; do
  iverilog -g2012 -s tb_v301_rtl -Ptb_v301_rtl.FULL_CAM=$variant -o /tmp/v301_$variant.vvp research/v301/v301_scoreboard_rtl.v research/v301/tb_v301_rtl.v
  vvp /tmp/v301_$variant.vvp
done
```

Only the Python portion has been executed locally because Icarus/Yosys are unavailable in the isolated local runtime. Hosted CI must supply independent RTL and synthesis evidence.
