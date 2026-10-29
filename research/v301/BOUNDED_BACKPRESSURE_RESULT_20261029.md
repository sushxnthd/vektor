# V301 bounded-upstream saturation sensitivity, 2026-10-29

**Decision: V301 eight-way CAM remains unjustified.** This is a new post-holdout sensitivity study, not a new prospective holdout and not a claim of a physical advantage. The frozen N1/N3 >=95% strong-control falsification from `SET4_FALSIFICATION_RESULT.md` remains binding. The purpose here is to replace the unbounded upstream producer with finite buffering and explicit source stalls.

## Reproducible experiment

```bash
python research/v301/bounded_backpressure.py --selftest
python research/v301/bounded_backpressure.py
```

The local selftest passed 12 conservation/backpressure configurations. The full experiment ran locally on 2026-10-29: 8 seeds (301-308), 40,000 cycles per seed, four potential return lanes, 8 completion-queue entries, 32 upstream slots, identical potential return streams across policies, and a one-write-port CAM/set4 control versus a two-bank/two-port comparator. The source is stalled if upstream slots are exhausted. A produced event is never dropped, and `produced = completed + inflight` is asserted. These are synthetic completion-path event rates, not GPU IPC or benchmark results.

| New sensitivity regime | Full CAM completed/cycle | Set4 completed/cycle | Set4 / CAM | Two-bank completed/cycle | Full CAM source-stall fraction |
| --- | ---: | ---: | ---: | ---: | ---: |
| S1 medium skew, short epoch | 1.822803 | 1.738406 | **95.3699%** | 1.378912 | 29.80% |
| S2 uniform high traffic | 1.063700 | 1.051916 | **98.8921%** | **1.876044** | 67.53% |
| S3 hot-warp demand | 3.200525 | 3.200525 | **100.0000%** | 1.110966 | 0.00% |
| S4 low offered load | 0.599025 | 0.599025 | **100.0000%** | 0.599028 | 0.00% |

Source-stall fraction for set4 is 33.05% in S1 and 67.89% in S2. Full CAM's S1 advantage is only 4.855% relative to set4; its S2 advantage is 1.120%. S3/S4 tie. The two-bank alternative dominates the uniform workload. The earlier overdriven drain-rate finding therefore was not simply an artifact of unbounded upstream storage, **but neither does bounded backpressure rescue V301 from the stronger set4 control**.

## Interpretation and limitations

- **Not independent prospective validation:** the S1-S3 regimes intentionally mirror the opened N1-N3 motifs, although the random seeds and buffering model differ. Do not count these as unseen predictions.
- **No new positive boundary law:** the occupancy expression `E[U] = sum_w(1-(1-a*p_w)^B)` predicts ingress collision counts, not queue throughput. The bounded experiment adds source-stall accounting but does not derive a validated predictive throughput boundary.
- **Simplified flow control:** potential returns denied by the upstream buffer are source-stalled rather than held as an explicit GPU pipeline state. The model does not represent warp issue, memory timing, deadlock cycles, actual scoreboard port counts, energy, or tile-level performance.
- **Equal storage is not equal silicon:** set4 and full CAM have eight entries each; the two-bank policy has two physical scoreboard writes/cycle. No matched mapped area, routed timing, switching power, or DRC exists for V301.
- **Scientific consequence:** the previously frozen strong-control threshold is still failed. Do not tune a new mask/epoch regime to rescue this CAM. The next authorized step is one bounded matched RTL/physical comparison against an optimized set4 implementation; retire if set4 is no worse in area/timing and maintains its >=95% throughput ratio. If physical validation cannot be obtained, label V301 *unjustified* and retire without a positive claim.

No RTX 5090 equivalence or GPU-level speedup is supported.
