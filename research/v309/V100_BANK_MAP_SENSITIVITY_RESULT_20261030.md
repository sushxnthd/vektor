# V309: authentic V100 SASS bank-map/port sensitivity result (2026-10-30)

**Research decision: NO HARDWARE PROMOTION.** A new physically informed negative screen removes most of the modeled single-port register-bank bottleneck. This is not measured GPU IPC, stalls, clock, area, or power.

## Reproduction and evidence

- Immutable original Purdue Tesla V100 Rodinia 2.0-ft archive: SHA-256 `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`.
- Protocol **committed before new full-corpus map sweep**: `BANK_MAP_SENSITIVITY_PROTOCOL_20261030.md`. Earlier modulo-bank results had been inspected, so these same applications are exploratory, **not prospective holdouts**.
- [Hosted run #40953345745](https://github.com/sushxnthd/vektor/actions/runs/40953345745) **passed** on `60ed8d0`: 3 model fixtures, 6 deliberately corrupted report mutations rejected, complete 3,937,565-row profile, independent audit.
- [Raw JSON artifact #12932492600](https://github.com/sushxnthd/vektor/actions/runs/40953345745/artifacts/12932492600): per-application full counts and independent checker output.
- Independent checker: 11 applications, 3,937,565 active rows, 22/55 mod2-vs-xor2 family-order inversions, 17/55 at B=4 (6 ties), 25/55 at B=8 (10 ties). Mapping-transfer robustness is **falsified for the two chosen hypothetical functions**, not for V100's empirically established bank map.

## Main physically informed negative screen

Count distinct within-instruction sources only once (strong free-broadcast control) and assume R255 bypass. Let `n_ib` be source demand at bank b. For P modeled bank reads per cycle, isolated service lower bound is `L_i=max_b ceil(n_ib/P)`, with L=0 for no reads. Count `max(0,L_i-1)` as *isolated extra bank read-service cycles*, not actual stalls.

| Bank map (hypothetical unless noted) | P=1 extra isolated read cycles | P=2 extra isolated read cycles | P=2 rows affected |
|---|---:|---:|---:|
| mod2 (V100 microbenchmark supported) | **568,740** | **39,413** | 39,413 |
| xor2 (counterfactual) | 459,561 | 1,746 | 1,746 |
| mod4 | 44,713 | 18 | 18 |
| xor4 | 365,918 | 1,278 | 1,278 |
| mod8 | 15,693 | **0** | **0** |
| xor8 | 160,181 | 18 | 18 |

For `mod2`, P=2 removes **93.0701%** of the P=1 isolated extra service count (568,740 -> 39,413). Only **1.001%** of active dynamic rows retain any modeled extra service. All observed per-instruction mod2 demands fit within three distinct sources per bank; the remaining P=2 events are exactly the three-same-bank case in this isolated model. In 6/11 Rodinia families, P=2 removes all modeled extra service.

The identity `568,740 = 529,327 + 39,413` independently reconciles the previous collision-bearing row count (529,327) with the additional read cycle on triple-same-bank instructions.

## Per-family physically informed mod2/P=2 screen

| Family | Active dynamic rows | P=1 extra cycles | P=2 extra cycles | P=2 affected-row share |
|---|---:|---:|---:|---:|
| Backprop | 365,335 | 34,821 | 4,096 | 1.121% |
| BFS | 136,983 | 14,103 | 0 | 0 |
| Heartwall | 234,447 | 38,709 | 2,550 | 1.088% |
| Hotspot | 1,219,773 | 223,246 | 31,659 | 2.595% |
| KMeans | 259,113 | 21,968 | 0 | 0 |
| LUD | 30,528 | 6,844 | 84 | 0.275% |
| Nearest Neighbor | 563,674 | 84,144 | 0 | 0 |
| Needleman-Wunsch | 51,816 | 12,232 | 0 | 0 |
| Pathfinder | 34,002 | 3,225 | 0 | 0 |
| SRAD v2 | 358,606 | 60,288 | 1,024 | 0.286% |
| Streamcluster | 683,288 | 69,160 | 0 | 0 |

**Prior-art correction:** Jia et al., *Dissecting the NVIDIA Volta GPU Architecture via Microbenchmarking*, arXiv:1804.06826 (2018), section 3.5, report two **64-bit** RF banks and index-modulo-two mapping on Volta. Their FFMA microbenchmark observes a conflict when all three 32-bit sources map to one bank. [Paper](https://arxiv.org/abs/1804.06826). Thus P=2 is qualitatively consistent with the published FFMA observation, but **64-bit width is not proof of unrestricted two-port operation for all SASS instructions**. The P=1 screen is too pessimistic as a universal V100 FFMA stall proxy. See `V100_BANK_MAPPING_PRIOR_ART_CORRECTION_20261030.md`, committed while the new sweep was running.

## What was falsified, and what was not

- **Falsified:** selecting hardware solely because modulo-two *one-port* demand appears large. Stronger, physically motivated bank-service capacity erases 93.07% of that isolated demand. Also, ranking stability cannot be assumed across counterfactual bank maps.
- **Not established:** V100 actual per-opcode stalls, collector timing, issue throughput, memory bandwidth, occupancy, tile-level gain, synthesis/timing/area/power, or any RTX 5090 correspondence.
- **No mechanism promoted:** V309 remains a qualification workstream. Prior retired V287/V296/V297-V308 mechanisms are not revived.

## Next decisive experiment

Reproduce the published FFMA two-bank microbenchmark behavior with an independent opcode-aware collector model, then calibrate against matching V100 performance counters or a validated simulator. Only after that identify a genuine residual bottleneck, freeze disjoint predicted-win and no-win workloads, and test one equal-resource hardware mechanism through RTL and physical synthesis. If no residual survives the strongest control, retire this bank-conflict avenue.
