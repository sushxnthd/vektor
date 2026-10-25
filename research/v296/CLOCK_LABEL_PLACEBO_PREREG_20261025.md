# V296 architecture-label placebo: frozen negative-control protocol (2026-10-25)

**Purpose:** determine whether the reported 3 ns versus 4 ns synthetic workload throughput difference is attributable to V296 arbitration or entirely to an assumed period assignment. This is a falsification of attribution, not a new architecture mechanism. V296 remains the sole provisional mechanism; V287 retired.

## Preregistered test before new-seed evaluation

The existing `matched_walltime_workload.py` simulator has one shared `greedy` bank/port arbitration algorithm, and its `replay(workload, period_ns, bandwidth_gbs, bucket)` takes **no architecture label**. Hold the identical absolute-time event list, resource limits, bandwidth and queue depth fixed. Compute T3 and T4 from independent replay calls at periods 3 ns and 4 ns. Evaluate four assignments:

- original labeling: serial=T4, V296=T3;
- clock swap: serial=T3, V296=T4;
- matched 3 ns: both=T3;
- matched 4 ns: both=T4.

**Predictions frozen before reading new-seed outcomes:** equal-clock candidate/serial ratios are exactly 1 at both clocks; the swapped ratio is exactly the reciprocal of the original ratio (within 1e-12 arithmetic tolerance). Thus this simulator cannot identify an architecture-specific throughput effect, regardless of whether the assumed clock difference causes a conditional performance change.

Frozen unseen synthetic cases, not GPU trace holdouts:

1. `clock_only_win`: seed 296501, valid=.95, hotspot=.35, persistence=.90, bandwidth=20 GB/s, bucket=64 bytes. Predict original-label ratio in [1.01,1.50] and equal-clock ratio exactly 1.
2. `bandwidth_no_win`: seed 296502, same event distribution, bandwidth=1 GB/s, bucket=64 bytes. Predict original-label ratio in [0.999,1.001] and equal-clock ratio exactly 1.
3. `hotspot_stress`: seed 296503, valid=.95, hotspot=.90, persistence=.98, bandwidth=20 GB/s, bucket=64 bytes. No preregistered directional period effect; exact label-invariance predictions still apply.

Existing simulator constants, 16 banks, 4 slots, 2 ports per bank, FIFO depth 8, 8 bytes per admitted request, 60,000 ns simulated, 12,000 ns burn-in, must not be modified. Preserve existing GPU holdouts sealed. Evaluate each frozen event list once per clock and reassign the resulting rates without regenerating events or adjusting traffic.

**Falsifiers:** any matched-period difference, nonreciprocal clock-swap ratio, failed bandwidth/FIFO/oracle invariant, or a frozen numeric range miss must be reported, not hidden. No period is claimed physically feasible: original matched postroute V296 and serial control both fail 3.5 ns setup, hold and capacitance gates. This test cannot establish GPU performance or replace the outstanding physical experiment.
