# V296 matched-real-time workload transfer: a 3/4 clock-period assumption does NOT yield 4/3 useful throughput (2026-10-25)

**Evidence:** deterministic *synthetic* timestamped trace simulator with independent exhaustive priority oracle; not a GPU trace, measured clock, measured power, or physically feasible V296 implementation. The original integrated V296 and serial one-hot designs both FAIL the 3.5 ns setup/hold/capacitance gate. No RTX-5090 comparison is justified.

## Protocol and prospective predictions

The protocol was frozen in commit `ab1972e0` **before** running prospective seeds 296201–296204. It fixes 16 RF banks, 2 reads/bank/cycle, 4 issue slots, FIFO depth 8, 8 bytes/wave, a finite memory token bucket, common absolute-time wave arrival timestamps, bank hotspot probability 0.35, persistence 0.90, 60,000 ns horizon and 12,000 ns burn-in. The serial baseline and candidate share identical offered waves per *real second*, not merely identical requests per cycle. Hypothetical periods 4 ns (serial) and 3 ns (V296) are illustrative **only**. The strongest actual physical serial control remains infeasible.

The calibration seed 296101 gave a 1.1922401x ratio at 20 GB/s, while 296102–296104 gave 1.000000x at 1 or 2.5 GB/s. Before opening independent seeds, the frozen acceptance ranges were [1.15,1.23] for the high-bandwidth conditional-win regime and [0.995,1.005] for the three bandwidth-limited no-win regimes.

## Prospective transfer results

| Independent synthetic seed | Sustained BW | Token bucket | Serial waves/ns | Candidate waves/ns | Ratio | Frozen gate |
|---:|---:|---:|---:|---:|---:|---|
| 296201 | 20 GB/s | 64 B | 0.733729167 | 0.867270833 | **1.182004x** | PASS conditional-win range |
| 296202 | 1 GB/s | 64 B | 0.125000000 | 0.125000000 | **1.000000x** | PASS no-win |
| 296203 | 2.5 GB/s | 16 B | 0.312479167 | 0.312500000 | **1.0000667x** | PASS no-win |
| 296204 | 2.5 GB/s | 128 B | 0.312500000 | 0.312500000 | **1.000000x** | PASS no-win |

All four used **exactly matched offered waves/ns**, with independent per-cycle exhaustive 2^4-subset checks, FIFO work conservation and traffic <= provisioned bandwidth. The 1280-state standalone oracle self-test passed locally. Seed 296201 offered 0.950270833 waves/ns to both implementations. The faster hypothetical clock reduced queue overflow but did not deliver the naive 33.333% clock-ratio improvement: its observed synthetic gain was **18.2004%**.

## Boundary and falsification

For a fixed-time arrival rate `lambda`, bytes/wave `b`, sustainable bandwidth `W`, feasible period `T_j` and achievable bank/FIFO admission capacity `q_j` waves/cycle, conservation requires

```
R_j <= min(lambda, W/b, q_j/T_j).
```

The key correction is that **q_j need not remain constant when T changes**, even if the arbitration semantics and bank resources are identical: fixed-time arrivals become differently bunched into cycles; bounded queues and bank-port conflicts change occupancy and drops. A naive `R_candidate/R_serial = T_serial/T_candidate` overstates the conditional gain in the high-bandwidth matched-time workload (1.333333 predicted vs 1.182004 observed). At 1 GB/s and b=8 B, `W/b = 0.125 waves/ns` is attained by both: the memory roof eliminates the hypothetical clock advantage entirely. At 2.5 GB/s the roof is 0.3125 waves/ns; finite-bucket quantization produces only a 0.0067% discrepancy in one case.

This is a **necessary capacity bound**, not a validated universal positive mechanism. The actual `q_j` is trace-, queue-, clock- and port-dependent and must be predicted prospectively from external traces. No positive V296 architectural effect is demonstrated: both variants make the same bank-admission decisions at identical clock and state, and all modeled gains come from assumed periods that have not been physically achieved.

## Reproduction and decision

```sh
python3 research/v296/matched_walltime_workload.py --self-test
python3 research/v296/matched_walltime_workload.py --evaluate calibration
python3 research/v296/matched_walltime_workload.py --evaluate prospective
```

The prospective ranges were frozen in `MATCHED_WALLTIME_BANK_MEMORY_PREREG_20261025.md` before prospective execution. These are newly generated synthetic holdouts, **not** the pre-existing sealed GPU workload holdouts. The executable simulator was committed at `57da2928`.

**Decision:** The conditional clock benefit is further bounded by queue/port dynamics and erased by realistic bandwidth ceilings in these synthetic regimes. Keep V296 the sole provisional mechanism, preserve V287's retirement, and do not relax the original physical failure. Immediate priority remains recovered extracted critical paths, symmetric matched repair and independently optimized equal-resource serial control; without feasible measured tile clocks and actual workload traces, the architecture gain remains unestablished. Kernellum PR #119 remains untouched.
