# V296 joint occupancy / area-packing / dependency falsification (2026-10-26)

**Evidence tier: prospectively frozen synthetic workload replay, not physical performance.** Protocol committed **before implementation/evaluation** in `c64723a5`; implementation `ff5ca70f`; reproducibility workflow `3f14b56f`. Two fixed random seeds 41719/41743, 500-cycle warmup, 4000 measured cycles, identical per-global-warp request streams across contestants. Local independent reference scheduler tests passed. Hosted workflow pending at report creation.

## New joint predictive envelope

For N hypothetical replicated slices, W total resident warps, L cycles of dependency latency, issue width I=4, shared byte bandwidth B, bytes per wave m, and global RF-read throughput R, the conservation ceiling is

```
Q_ideal <= min(N*I, W/L, B/m, R/2)     [waves/cycle, assuming shared rates expressed per cycle]
throughput <= f * Q_ideal
```

This is an **upper bound**, not a sufficient law for achievable throughput. Realized bank conflicts, scheduler control, latency, queueing and cross-slice load imbalance reduce throughput. The experiment independently generates requests and enforces per-slice 16-bank/2-port constraints rather than using the bound as a throughput oracle.

Mapped-area hypothesis: 17 serial slices consume **167363.742 um²**; 18 candidate slices consume **167158.656 um²** (205.086 um² under budget). A 19th candidate slice does not fit. These are *mapped-cell-only* numbers from earlier measured slice syntheses, **not** a routed replicated tile, matched total physical area, or a feasible 3.5 ns clock. Both architectures admit identical waves at identical readiness and resources; the only synthetic difference is the candidate's hypothetical extra slice and the symmetric operand-capture latency L=2 versus serial L=1.

With N_serial=17, the ideal serial issue ceiling is 68 waves/cycle. Even a perfect candidate cannot exceed that **ideal** ceiling unless W>136; it cannot reach its own 72-wave/cycle ceiling unless W>=144. Crucially, W>=144 is **not sufficient** because ports and scheduler conflicts remain. These conditions must not be misrepresented as a universal no-win threshold against a real port-constrained serial control.

## Frozen paired replay results

All figures are useful throughput change at equal hypothetical clock except the explicitly counterfactual +7% candidate period row.

| Fixed total warps / regime | Seed 41719 | Seed 41743 | Decision |
|---|---:|---:|---|
| W=32, distributed banks | -48.7738% | -48.7249% | Preregistered no-win, confirmed |
| W=136, distributed banks | -5.8925% | -5.8705% | Boundary probe, negative |
| W=140, distributed banks | -3.6234% | -3.6034% | Boundary probe, negative |
| W=144, distributed banks | -1.3533% | -1.3261% | **Ideal occupancy bound is not sufficient** |
| W=180, distributed banks | +5.2942% | +5.2979% | Preregistered conditional win, confirmed |
| W=180, shared cap 25 waves/cycle | 0.0000% | 0.0000% | Preregistered no-win, confirmed |
| W=180, candidate clock period +7% | -1.5942% | -1.5908% | Counterfactual no-win, confirmed |
| W=180, 80% hot-bank probability | +5.4384% | +5.5006% | Boundary probe; shared traffic not modeled |

At W=144, serial admits 67.981/67.982 waves/cycle while the candidate admits 67.061/67.080; the ideal 72 candidate slots are **not filled**. At W=180 the candidate admits 71.600/71.602 against serial 67.999, for +5.29%, below the naive +5.882% area-packing gain. Under shared cap 25, both useful rates saturate and the gain is exactly zero.

## Independent checks and limits

The executable `python3 research/v296/joint_occupancy_area_packing.py --self-test --evaluate` compares the fast scheduler against an independent dictionary-based event-state oracle on 27 randomized small configurations (three seeds, three slice counts, three latencies), verifies exact single-warp cooldown, bank read-port conservation, area floor inequalities, and frozen prediction signs. It writes a complete machine-readable per-seed record and per-slice warp distributions. Local prototype passed; hosted execution of the committed version is pending.

The synthetic model omits SRAM macros, wire delays, cross-slice interconnect, cache/memory effects, inter-warp divergence, power, bypass, instruction mix, realistic warp residency, physical clock closure, and dynamic bandwidth backpressure. Shared-cap accounting is a fluid-server ceiling, not a transaction-level memory simulator. Two deterministic seeds do not establish a statistical confidence interval. A per-warp request stream is paired, but the two variants reach different positions within that stream over the fixed measurement window.

## Architectural decision

**Do not claim a GPU gain.** This result tightens the optimistic area-reinvestment story: the extra candidate pipeline stage requires enough *total resident warps* to fill an additional hypothetical slice; W=144 still loses in port-exact replay, while W=180 gains only under abundant shared bandwidth and hypothetical feasible clocks. A 7% candidate clock-period regression erases the gain. V296 remains the sole provisional mechanism; V287 retired.

The decisive next step is still matched physical closure against the strongest independently optimized serial control, including the fifth-stage serial repair, then replicated tile area/RC, actual occupancy and bandwidth, and prospective unseen real workloads. The existing integrated physical run 40309580865 was still in progress at inspection. Preserve all failed gates; no RTX-5090-equivalence or power claim.
