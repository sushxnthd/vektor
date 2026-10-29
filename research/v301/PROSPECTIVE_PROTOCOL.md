# V301: epoch-safe associative GPU completion scoreboard (provisional)

Frozen before holdout seeds 101-120 are opened. Date: 2026-10-29.

## Mechanism and falsifiable causal hypothesis

GPU sector-return events may target the same warp and instruction epoch. If the scoreboard uses a single read-modify-write completion port, independently writing every return can cause a write-port bottleneck. V301 merges equal `(warp_id, epoch_id)` completion masks into one of eight outstanding accumulator entries, using bitwise OR. Merging across different epochs is forbidden. This requires eight parallel key comparisons, an OR update path, a priority encoder and queue state. There is no assumption that contemporary production GPUs have this exact scoreboard bottleneck.

**Baseline controls**: unmerged FIFO with the same eight entries and one scoreboard port; four-lane ingress-only merger with the same port; two-way four-set associative merger with eight entries and one port; and two-bank scoreboard with eight entries, one write port per bank (stronger port count, requires physical area matching before claims). All policies have four incoming return lanes, lossless producer backpressure and identical input streams. V301 is `queue_merge` in the simulator. No claims of equal silicon area before synthesis.

## Predictive boundary

For a full batch of B independent warp returns with warp probability distribution p_w, the expected number of unique destinations is `U(B)=sum_w[1-(1-p_w)^B]`; the theoretical intra-batch merge reduction is `B-U(B)`. For two returns the merge probability is `sum_w p_w^2`. With epoch boundaries, effective destination is `(warp,epoch)` rather than warp. These are exact ingress-batch laws, **not** predictions of the entire queue-merger's throughput. In particular, occupancy, arrival rate, producer backpressure, number of scoreboard ports, and epoch duration determine whether fewer writes translate to speedup. Do not fit a queue-throughput law after observing holdout outcomes.

## Opened pilot only

Four seeds 0-3; 5000 offered cycles; four return lanes; eight entry queue. `medium` (`offered=.55, warps=32, hot=.5`) gives V301 ~2.196 event/cycle vs 1.943 for set2 and 1.329 for two-bank control; `uniform_high` (`.9,256,0`) gives V301 ~1.032 vs two-bank ~1.873; `hot_high` (`.9,16,.9`) V301 ties set2 near 3.601. These are lossless synthetic **drain-time** rates, not sustained GPU execution throughput or actual physical design measurements.

## Frozen holdouts (never retune against these)

Run `python research/v301/scoreboard.py --holdout` once after this protocol and code have been committed. All use seeds 101-120, 5000 offered cycles, four lanes, eight-entry queues.

- H1 predicted win: offered .60, 48 warps, hot-warp probability .55, epoch period 1024. V301 must exceed **both** set2 by >=5% and two-bank by >=10% in mean event drain rate. This is a hypothesis, not a result.
- H2 predicted no-win: offered .90, 256 warps, uniform, epoch 1024. V301 must be no faster than two-bank (within 2% margin); any positive claim here fails the model.
- H3 low-load negative control: offered .20, 32 warps, hot .5. V301 drain-rate gain over FIFO must be <=2%.
- H4 strong set2 tie: offered .95, 16 warps, hot .9. V301 must improve over set2 by <=2%.
- H5 fast epoch: offered .60, 48 warps, hot .55, epoch period 16. Check exact conservation; performance may degrade, and it is not a win gate.

**Survival gate:** H1 + H2 + H3 + H4 all pass; all five runs preserve bit-exact `(warp,epoch)` OR completion. The proposed mechanism remains unvalidated until matched RTL, mapped area, electrical/RC timing, control-energy proxy, queue-level sensitivity, and a real GPU workload consequence pass. Retire V301 if strong physically equal-resource controls erase its gain. Even a positive synthetic result alone cannot establish novelty; prior work on GPU memory divergence, operand collectors, coalescing and scoreboard optimization must be audited.

## Reproduction

`python research/v301/scoreboard.py --selftest`
`python research/v301/independent_audit.py`
`python research/v301/scoreboard.py` (opened pilot)
`python research/v301/scoreboard.py --holdout` (prospective; only after frozen commit)

Known limitations: no real memory latency, no SM scheduling, no real RF or scoreboard layout, no power model, no measured GPU traces, and a deliberately narrow one-port bottleneck. `mean_oldest_entry_age` is an oldest-merged-entry proxy, not per-event latency.

## Prior-art boundary

Existing research already addresses GPU memory-divergence-aware scheduling and operand-collector/bank bandwidth: SC'14 Managing DRAM Latency Divergence (DOI 10.1109/SC.2014.16), MeDiC (arXiv:1804.11038), Triple-A (IEEE ESL 2024), and Warped-Compaction (HPCA 2025). The event-merging primitive itself is not claimed as novel. A defensible result requires a nontrivial matched-physical advantage and a demonstrated unaddressed scoreboard bottleneck.
