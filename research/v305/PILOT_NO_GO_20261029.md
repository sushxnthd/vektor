# V305 pilot no-go: demand-aware MSHR reservation adds no useful throughput

Date: 2026-10-29. Evidence tier: **local synthetic simulation and hand-calculated tests only**. This is not RTL, physical timing, GPU IPC, or measured DRAM behavior.

## Prospective integrity

The protocol was committed at `fc013bf0` before implementation and pilot evaluation. The pilot uses seeds 1–4 only. **Frozen holdout seeds 101–120 were never opened.** No thresholds or baselines were changed after observing pilot results.

Run from repository root:

```sh
python3 -m unittest discover -s research/v305 -p 'test_*.py' -v
python3 research/v305/simulator.py --pilot
```

Five hand-calculated/determinism tests passed locally. The simulator asserts no duplicate admission, full conservation, finite MSHR occupancy, partition response-port limits, and empty queues after final drain.

## Pilot, 4 seeds × 1200 offered cycles per regime

Mean rate is **all completed requests / total cycles including drain**. This is a synthetic memory-completion rate, not GPU IPC.

| Regime | FIFO | RR | Fixed quotas | Shortest latency | V305 guard | V305 vs best control |
|---|---:|---:|---:|---:|---:|---:|
| W1 slow-hot (48/12/12/12), p_hot=.70 | 0.319778 | 0.319702 | 0.088602 | 0.319689 | 0.319714 | **-0.0201%** |
| N1 uniform (24/24/24/24) | 0.497883 | 0.497943 | 0.481011 | 0.497883 | 0.497943 | **0.0000%** |

W1 mean p99 end-to-end synthetic latency: FIFO 5089.5 cycles, RR 5076.25, fixed 21380.5, shortest 5080.75, guard 5079.5. N1 mean p99: FIFO 2843.75, RR/guard 2862.5, fixed 2917. Peak 32-entry ingress queues saturate in the N1 pilot; upstream demand is retained rather than dropped.

**Frozen W1 survival requirement:** >=5% improvement over strongest equal-resource control. **Observed: -0.0201%.** V305 fails by a wide margin. It is retired without opening the holdout or investing in RTL.

## Mechanistic interpretation

The proposed reservation guard only changes round-robin admission when some *waiting* partition has zero in-flight requests and the pool is almost full. Under sustained backlog, each active partition normally already owns at least one MSHR, so the guard becomes exactly the round-robin control. When the slow hot partition dominates final drain, reserved capacity cannot improve the slow partition's response-latency bound. Fixed quotas severely underutilize MSHRs when offered load is skewed.

The necessary occupancy bound `T_i <= min(m_i/L_i, b_i)` remains valid, but **does not imply a positive speedup**. No compact positive law survived. The experiment cannot support a novelty or hardware-performance claim.

## Limitations and prior art

The model has synthetic deterministic per-partition latency, two request sources, one response per partition per cycle, and 12 total MSHRs. It lacks actual cache hits, memory coalescing, DRAM row state, realistic interconnect timing, writeback interference, occupancy coupling and measured traffic. The pre-generated exogenous trace is buffered at upstream sources; it does not model an application that stops generating while blocked. P99 numbers are dominated by overloaded synthetic queues.

MSHR reservation, memory scheduling and GPU throttling are established research areas. Relevant baseline context: [GPGPU-Sim manual](https://gpgpu-sim.org/manual/index.php/Main_Page) and [GPU partitioning/operand-collector analysis (HPCA 2023)](https://engineering.purdue.edu/tgrogers/publication/barnes-hpca-2023/barnes-hpca-2023.pdf). Neither is evidence that V305 is novel.

## Decision

**NO-GO at pilot.** Keep the code and negative result in the unmerged research branch. Do not run V305's frozen holdout as a post-hoc salvage attempt; do not promote to RTL or synthesis. Future candidates should first reproduce a workload bottleneck in a validated simulator or hardware microbenchmark before allocating a new mechanism.
