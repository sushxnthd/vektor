# V296 scaling-crossover prospective holdout: negative result (2026-10-24)

**Decision: SIMPLE_MAPPED_CROSSOVER_LAW_FALSIFIED.** This is a scientific falsification, **not** a CI/tool failure. The frozen 14-configuration sweep completed its RTL oracles and Nangate45/Yosys/ABC synthesis. The independent evaluator exited 3 because the preregistered quantitative prediction criteria failed. Preserve this result without tuning the original fit or changing the original holdouts.

- Frozen protocol: `SCALING_CROSSOVER_PREREG_20261024.md`.
- Completed failed-gate run: https://github.com/sushxnthd/vektor/actions/runs/40063326884
- Full 61-file raw evidence artifact: https://github.com/sushxnthd/vektor/actions/runs/40063326884/artifacts/12548178469
- Artifact SHA-256: `df25a04baf6d1473e9859fca0ee3f977bb8eaa5307e94c42a017410273ba4010`.
- Existing executable frozen evaluator: `scaling_crossover_audit.py`. Additional independent falsifier: `scaling_holdout_forensics.py`.
- **Independent raw replay completed:** downloaded the original artifact ZIP, verified its SHA-256 digest, extracted all 61 files, and executed `python3 research/v296/scaling_holdout_forensics.py <artifact>/scaling_crossover_audit.json --logs-dir <artifact>`. The checker reconciled each of the five held-out areas against the corresponding raw Yosys log, verified the independent RTL-oracle PASS markers, recomputed errors and winner labels, and returned `FROZEN_AREA_LAW_FALSIFIED_AND_SINGLE_RATIO_THRESHOLD_FALSIFIED`. This replay is not a new holdout.

## Frozen quantitative test

The fixed training set contained nine (bank-index bits, issue-slot count) configurations; five different configurations were withheld from the two-parameter area fit. The fit predicted area from `X_pair=B[2S(S-1)+S]` and `X_onehot=2S 2^B`. Both fitted slopes were positive, but both fitted intercepts were **negative** (pairwise -24.482, one-hot -115.625 square micrometers), already warning that the unmodified affine laws cannot extrapolate to zero complexity.

| Banks | Slots | Pairwise mapped area (um2) | Serial one-hot mapped area (um2) | Pairwise saving vs one-hot | Correct winner prediction? |
|---:|---:|---:|---:|---:|:---:|
| 4 | 4 | 175.826 | 133.532 | **-31.673%** | yes (one-hot) |
| 8 | 8 | 1079.162 | 764.218 | **-41.211%** | yes (one-hot) |
| 16 | 8 | 1348.886 | 1710.114 | **+21.123%** | yes (pairwise) |
| 32 | 2 | 53.998 | 468.692 | **+88.479%** | yes (pairwise) |
| 64 | 8 | 1764.378 | 6514.872 | **+72.918%** | yes (pairwise) |

The original prediction got **5/5 winner labels**, but the original *quantitative* gate required both models to have mean absolute relative error <=20% and worst error <=30%. Pairwise errors were **11.878% mean, 28.393% maximum** (passes its individual error gates). One-hot errors were **25.208% mean, 45.522% maximum** (fails both). Therefore the combined **positive area-law claim fails**. Do not relabel the result as a pass on the strength of the winner labels.

## A stronger falsification: structural-ratio thresholds cannot explain all five outcomes

A tempting zero-fit rule would predict a pairwise win when the ratio `R=X_onehot/X_pair` exceeds a constant. But at **4 banks, 4 slots**, `R=0.571429` and pairwise **loses**, while at **16 banks, 8 slots**, `R=0.533333` and pairwise **wins**. Thus no monotone *increasing* single-threshold rule on R separates the observed cases. A monotone *decreasing* rule also fails: at **32 banks, 2 slots**, `R=4.266667` and pairwise wins, while at **8 banks, 8 slots**, `R=0.355556` and pairwise loses. The ratios are gate-count proxies, not measured gates; synthesis sharing, constant folding, fanout and topology matter.

The structural crossover is real for **these mapped microbenchmarks only**; it does not establish an accurate transferable quantitative law, post-route advantage, energy reduction, scheduler throughput gain, or superiority over every possible equal-resource controller. These arbiters omit scheduler/wave-selection logic, clock trees and RF macro/port costs.

## Consequence and next pre-outcome experiment

1. Retain **V296 as the sole provisional mechanism** while the separate control-advantaged high-RC detailed-route experiment remains pending. **V287 stays retired**. The mapped-area-law failure alone does not prove V296 physically inferior at the target configuration; it forbids the proposed *universal simple area law*.
2. Any replacement positive law must use an explicitly stated mechanistic decomposition (e.g., decode, bank occupancy state, pair comparisons and priority depth), compare against strong synthesized controls, and be frozen **before** new, genuinely unseen parameter configurations are synthesized. The five holdouts above are now opened and may be used for exploratory diagnostics but never recycled as prospective validation. No post-hoc fitted model is validated here.
3. Suggested untouched validation configurations for a separately preregistered next study: (B,S)=(3,6),(4,6),(5,6),(6,3),(7,4). Do not synthesize them until the replacement formula, training data, area error thresholds and control definition are frozen. These are structural parameter tests, not the separately sealed workload holdouts.
4. For a GPU-level positive law, measured frequency and resource effects must enter an occupancy/bandwidth/port-pressure throughput model. Because both controllers implement **identical greedy admission decisions**, V296 cannot claim an instruction-count or memory-traffic advantage solely from this arbiter swap. A win must survive matched physical closure and either measured clock/area improvements or independently demonstrated system consequences.
5. Do not merge PR #13 or claim tile-level, power, or RTX-5090-equivalent results. Preserve the earlier electrical failures and current four-way control test as separate gates.

**Evidence tier:** independently checkable hosted mapped combinational area and RTL simulation; no new physical-signoff or measured GPU throughput result.
