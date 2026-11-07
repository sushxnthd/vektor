# V317 rotating-priority strong-control RTL: hosted physical proxy and transfer (2026-11-01)

## Source-pinned result

[Hosted rotating RTL, three-way matched Yosys and frozen transfer run #41278385811](https://github.com/sushxnthd/vektor/actions/runs/41278385811), at source commit `4488bb6fbb930fbb30a675a6189b7842a7deb876`, completed the independent **16,449-case Icarus RTL oracle**, matched generic synthesis, cost parser and frozen streaming transfer steps successfully. The source-pinned log reports:

| Implementation | Generic cells | Generic logic levels | Flip-flops | Ratio to fixed cells |
|---|---:|---:|---:|---:|
| Fixed-priority source RTL | 1,321 | 49 | 0 | 1.0000x |
| Rotating-priority strong simple control | **1,613** | **58** | **2** | **1.2210x** |
| Exact maximum-cardinality challenger | 5,116 | 72 | 0 | 3.8728x |

The preregistered prediction that rotation would be smaller and shallower than exact **survived** this generic synthesis comparison. This is **not** standard-cell area, routed delay, timing closure, electrical signoff or a GPU tile comparison. The 58 vs 49 logic levels are not a measured clock penalty.

The independent full-stream cross-check was added after the first hosted run; it must pass on a later final-head run before the entire result is labeled independently reproduced.

## Frozen unseen synthetic workload

30,000 cycles, 3,000-cycle warmup, identical pregenerated arrivals, four issue FIFOs, two physical reads per bank, no execution/memory latency.

| Frozen unseen regime | Fixed completed | Rotating completed | Oldest-first completed | Age-aware exact completed | Rotating/fixed |
|---|---:|---:|---:|---:|---:|
| Four-bank p=.52 | 56,127 | 56,144 | 56,141 | 56,145 | 1.000303x |
| Four-bank p=.60 | 60,899 | 64,784 | 64,774 | 64,785 | 1.063794x |
| Private-bank p=.55 | 59,470 | 59,470 | 59,470 | 59,470 | 1.000000x |

The no-material-win and private-bank negative-control predictions survived. The stressed p=.60 regime shows improved finite-horizon service and backlog relative to the deliberately unfair fixed-priority source RTL, **not** a new architecture gain: oldest-first greedy achieves essentially the same completed work. In the p=.60 run, final backlogs are fixed 4,293 / rotating 16 / oldest-first 17 / age-aware exact 6, and p99 latency is 6,811 / 23 / 11 / 8 cycles. The apparent fixed-priority loss is a queue fairness effect.

## Clock/area break-even boundary, explicitly conditional

Let `g` be the synthetic completed-service ratio, `c=f_rot/f_fixed` the **unknown** achieved clock ratio, `a` the assumed fraction of baseline tile area occupied by the fixed arbiter, and `r=1613/1321=1.22104466` the **generic-cell proxy** ratio. The conditional throughput/area factor is

`E = g*c / [1+a*(r-1)]`.

At p=.60, `g=1.06379415`: **any achieved clock reduction exceeding 5.996% erases the raw completed-service gain**, even before area penalties. At p=.52, the break-even clock penalty is only about **0.0303%**. These are sensitivities, not measured timing. At assumed `a=1%`, the illustrative tile area factor is 1.0022104; this is not an area estimate.

The useful boundary is classical queue stability/fairness, not a novel positive hardware law: when both schedulers are stable and drain arrivals, long-horizon completed work is constrained by offered work; under fixed-priority starvation near saturation, a fair policy can avoid runaway backlog. Because a simple oldest-first baseline matches rotation, no distinctive mechanism is established.

## Decision

**Exact maximum-cardinality selector: KILL as architecture candidate.** It is more expensive and deeper in generic synthesis, and failed its frozen completed-work win.

**Rotating priority: RETAIN AS STRONG SIMPLE CONTROL ONLY.** It is functionally correct in the tested model and cheaper than exact, but not novel, not equal-area or equal-clock validated, and not a measured GPU IPC improvement.

Next candidate must exceed rotating and oldest-first at matched area/clock and survive physical wire/load and workload sensitivity. Do not make RTX-5090-equivalence claims. Kernellum PR #119 remains untouched.
