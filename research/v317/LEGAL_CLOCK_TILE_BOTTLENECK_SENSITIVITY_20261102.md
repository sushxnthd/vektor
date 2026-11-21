# V317 routed controller-to-tile clock bottleneck sensitivity (2026-11-02)

## Evidence and scope
Reproducible [calculator](rtl/legal_clock_tile_sensitivity.py) committed at `44ac7ff`. It reuses five previously routed 32-wave Nangate45 integrated-controller rows (seeds 7, 19, 37; seed-7 density add-ons 0.05 and 0.35). **These are three placement seeds, not five independent seeds.** Their existing 2.000-ns setup slacks and routed standard-cell areas are measured; the following alternative clock periods and tile critical paths are **arithmetic sensitivity scenarios**, not new physical routes or measured GPU throughput.

Let `T_source = 2.000 ns - slack_source/1000`, `T_pair = 2.000 ns - slack_pair/1000` for slack in ps. If an independent unmeasured tile path has period `T_other`, the conditional **clock-only** service ratio at identical work/cycle is

`R_clock(T_other) = max(T_source,T_other) / max(T_pair,T_other)`.

This ratio is **not IPC** and omits SRAM, clock tree, power, memory and area reinvestment. It is a necessary timing bottleneck calculation, not a novel architecture mechanism.

## Five-row measured inputs and deterministic sensitivity
Across five existing routed configurations:

- Source controller critical periods: **2.001483–2.006600 ns**.
- Pairwise controller critical periods: **1.893696–1.939513 ns**.
- Pairwise routed standard-cell area reductions: **10.600–12.765%**.

| Hypothetical independent tile path period | Clock-only pairwise/source throughput ratio range |
|---|---:|
| 1.800 ns | 1.03302–1.05775x |
| 1.950 ns | 1.02640–1.02903x |
| 2.000 ns | 1.00074–1.00330x |
| **2.050 ns** | **1.00000x for all five** |
| **2.200 ns** | **1.00000x for all five** |

At a fixed unchanged netlist, relaxing the timing target to 2.050 ns would shift the source setup slack to **+43.400 to +48.517 ps**. At 2.200 ns it would shift to **+193.400 to +198.517 ps**. These shifts do **not** guarantee legal P&R after target-dependent optimization, nor prove hold/electrical closure. The [separately frozen four-route experiment](FROZEN_LEGAL_CLOCK_CROSSOVER_CHALLENGE_20261102.md) will measure that directly; the prospective physical outcomes remain pending.

## Falsification boundary
The earlier integrated-controller Fmax gain of approximately 4% cannot be promoted into a tile clock or GPU throughput gain unless the controller is the limiting tile path. In all five prior physical rows, **any independent tile critical path of at least 2.0066 ns eliminates the clock advantage entirely**. A hypothetical 2.200-ns other-tile path therefore yields 1.000x, even though pairwise has a faster controller.

If the upcoming 2.050/2.200-ns matched routes show the source legally closes timing and pairwise retains >=7% area reduction, the defensible result is an implementation-area advantage with possible *conditional* tile-replication value, **not a direct throughput mechanism**. If area savings collapse under the legal original, kill the materiality claim. No 5090-equivalence or real GPU IPC claim.
