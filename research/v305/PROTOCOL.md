# V305 preregistration: demand-aware partition guard for finite GPU MSHRs

Status: PROSPECTIVE; no V305 holdout results inspected at freeze.
Mechanism: an elastic reservation guard for a shared miss-status holding register (MSHR) pool. Four memory partitions share exactly twelve MSHRs. Each request owns one MSHR until its response; partition-specific response bandwidth and service latency are explicit. The candidate allows idle partitions' reserved credits to be borrowed, but when a partition has waiting demand, admission to other partitions must preserve one free credit for it. No cancellation or eviction of in-flight misses.

This is a *research hypothesis*, not a novel GPU mechanism claim. MSHR partitioning, throttling, and memory-aware scheduling have substantial prior art. The target is a falsifiable bottleneck boundary and a realistic controller cost gate.

## Locked comparison and evidence tiers

Equal-resource controls: (1) globally oldest eligible request, (2) round-robin partition selection with no reservation, (3) fixed equal three-MSHR quotas per partition, and (4) a work-conserving partition-aware selection policy with equal MSHR budget. No policy may use future arrivals or free additional MSHRs. A mechanism cannot survive solely by beating FIFO.

Pilot seeds 1-4 may be used to debug and reject the candidate; do not tune to the frozen holdouts. Holdout seeds 101-120 must remain unopened until implementation, metrics, and baseline choices are committed.

All workload traces are pre-generated from the same seeds for all policies; every request must complete. Model 4 partitions, 12 MSHRs, 1 response/partition/cycle, finite per-partition ingress of 32 requests with backpressure to the source. Report completed requests per cycle (including final drain), offered attempts, blocked source cycles, p95/p99 end-to-end request latency, per-partition fairness, peak pending, and MSHR occupancy. No metric is GPU IPC.

## Frozen regimes

W1 predicted-win: one slow hot partition (latency 48) with three fast sparse partitions (latency 12), 70% of requests targeting slow; bursty arrivals. Hypothesis: reserving credits improves fast-partition service and overall completion rate against global FIFO/round-robin. Survival requires >=5% higher total completion rate than **the best equal-resource control**, and no more than 10% p99-latency regression on any partition.

N1 predicted-no-win: uniform partitions (latency 24 each), uniform demand. Expected advantage <=2% over best control. A regression >2% is a no-go.

S1 sensitivity: vary slow partition latency [24,48,96], hot probability [0.4,0.7,0.9], MSHRs [8,12,16], per-partition ingress depth [8,32], and bank response bandwidth [1,2]. Changes to these ranges after observing holdouts invalidate the prospective claim.

## Predictive law to test

With occupancy m_i, mean completion latency L_i, and per-partition response capacity b_i, each partition satisfies T_i <= min(m_i/L_i, b_i). Shared occupancy sum_i m_i <= M. Any claimed positive gain must predict where fixed quotas underutilize M while global admission starves low-latency partitions. Compare this law with measured holdout rates, report errors and failed regimes. This bound is necessary but not sufficient for positive novelty.

## Hard physical gate

If synthetic survival succeeds: clocked RTL against equal-state RR/fixed-quota controls, independent conservation/ordering checker, Nangate45 matched area/timing, realistic fanout/RC, power proxy, then tile-level performance. Kill if clock/area or realistic memory bandwidth removes gain. No RTX-5090 equivalence claim.
