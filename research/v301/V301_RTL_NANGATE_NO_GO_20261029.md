# V301 no-go: independent RTL equivalence and matched mapped-area falsification (2026-10-29)

**Decision: RETIRE the eight-way associative V301 mechanism.** The previously frozen N1/N3 strong-control throughput falsification remains binding; the new clocked RTL/mapped-area evidence gives no reason to override it. This is not a completed routed GPU implementation.

## Hosted evidence

[GitHub Actions #40835743046](https://github.com/sushxnthd/vektor/actions/runs/40835743046) completed successfully on the existing V301 research branch, with [raw artifact #12879859054](https://github.com/sushxnthd/vektor/actions/runs/40835743046/artifacts/12879859054). The run reproduced the prior simulator and bounded-source tests, installed Icarus/Yosys, generated independent reference vectors, ran both clocked RTL policies and mapped both with the **same pinned Nangate45 typical Liberty** (OpenROAD-flow-scripts revision `eda8e552974d47a12616294dddf4012d892548d3`). Yosys reported zero structural problems for both.

| Metric | Two-set, four-way functional control (FULL_CAM=0) | Eight-way CAM V301 (FULL_CAM=1) |
| --- | ---: | ---: |
| Clocked oracle agreement | 1,024 / 1,024 cycles | 1,024 / 1,024 cycles |
| Nangate45 mapped standard-cell area (um^2) | **5,839.232** | **6,548.654** |
| Mapped cells | 4,402 | 4,990 |
| Flip-flops | 180 | 180 |
| Yosys structural checks | 0 problems | 0 problems |

V301 incurs **12.149% more mapped area** than the unoptimized functional set4 control, for the same 180 state bits. This is an isolated macro mapped-cell-area proxy, not GPU-wide silicon area or power.

## Previously frozen throughput falsification

The preregistered strong-control N1/N3 test found set4/full-CAM event-rate ratios of **95.340%** and **100.000%**, respectively. A separate post-holdout 32-entry bounded-upstream sensitivity found **95.3699%** in medium skew and **98.8921%** in uniform traffic, with ties in hot/low-load regimes. Two-bank scheduling remained substantially stronger in uniform traffic. These are synthetic completion-path rates, **not GPU IPC**.

The combination of (1) the previously failed >=95% strong-control survival gate, (2) an independently clocked, functionally correct RTL implementation, and (3) 12.149% mapped-area overhead versus even an **unoptimized** set4 comparator makes further investment in the eight-way CAM unjustified. Do not retune the opened holdouts or promote the mechanism.

## Limitations, preserved explicitly

- The set4 RTL is a functional comparator over a compacted queue, **not a fully optimized physically partitioned set4 macro**. Its area could be improved; the existing comparison therefore does not favor V301.
- The clocked test checks admitted input and output equivalence. Rejected random test-vector events are not reoffered, so it is not a lossless producer model.
- No placed/routed area, clock tree, extracted-RC setup/hold, DRC, slew, capacitance, switching power, or full tile consequence was measured. A 12.149% mapped-area penalty **does not establish a timing penalty**.
- The assumed one-write-port scoreboard bottleneck is unverified for commercial GPUs. No novel throughput boundary beyond elementary ingress occupancy was validated on real traces.
- The absolute mapped areas are high for a tiny controller because the reference RTL uses a dynamically indexed compacted queue; do not interpret these as optimized hardware implementations.
- The kill decision is a **competitive architectural no-go under the frozen synthetic and mapped-area evidence**, not a proof that CAM aggregation is impossible or universally inferior.

## Reproduction

```sh
python3 research/v301/v301_rtl_oracle.py
for variant in 0 1; do
  iverilog -g2012 -s tb_v301_rtl -Ptb_v301_rtl.FULL_CAM=$variant -o /tmp/v301_$variant.vvp research/v301/v301_scoreboard_rtl.v research/v301/tb_v301_rtl.v
  vvp /tmp/v301_$variant.vvp
done
```

Pinned Yosys mapping and raw evidence are in `.github/workflows/v301-pilot.yml` and its linked artifact. **Retire V301, close the draft PR unmerged, preserve all evidence, and do not claim RTX-5090 equivalence.** The next active mechanism requires a fresh prior-art audit and a frozen predictive boundary before prospective evaluation.
