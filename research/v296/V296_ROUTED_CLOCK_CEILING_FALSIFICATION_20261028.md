# V296 routed-clock headroom versus retiming: post-hoc sensitivity falsification (2026-10-28)

**Decision:** Do not treat V296's successful routed timing as evidence of a meaningful frequency-based GPU speedup. At the frozen 3.5 ns clock and +50 ps setup guard, the completed candidate has only **16.661 ps (D4)** and **9.643 ps (D8)** of fixed-path frequency headroom. Under unchanged path identity, RC, and hold constraints, this permits at most **0.4783% (D4)** or **0.2763% (D8)** clock-frequency uplift. Those are optimistic mathematical ceilings, not measured faster clocks. The strongest D4 serial control fails setup and hold, and the D8 serial control timed out, so no physically feasible matched pair or GPU speedup is established.

## Source and evidence tier

Source: original [four-way routed GitHub Actions run 40646515864](https://github.com/sushxnthd/vektor/actions/runs/40646515864), frozen source commit `84245c21f485c191aea7d352652c0ef036d6d047`. This experiment uses **only** completed original-job-log candidate setup/area measurements, not the incomplete independent aggregate. D4 candidate: setup +66.661 ps, area 19,543.019647 µm². D8 candidate: setup +59.643 ps, area 26,723.956381 µm². The D4 serial control fails setup/hold; D8 serial is censored (exit 124). Original routed data are post-CTS detailed-route OpenRCX, **not silicon signoff**. This new analysis is post-hoc, not preregistered and not an unseen-workload evaluation.

## Necessary fixed-path frequency law

At nominal period `P=3500 ps`, extracted setup slack `S`, and required guard `G=50 ps`, reducing the period by `x` reduces fixed-path setup slack by `x`. Therefore:

`x <= S-G; P_min=P-(S-G); f_new/f_old <= P/[P-(S-G)]`.

This is an **upper bound conditional on no physical reoptimization**; changing placement, RC, clock tree, hold, or critical-path identity invalidates the extrapolation and requires a new routed measurement.

| Candidate | Guard headroom | Fixed-path shortest period | Optimistic max frequency uplift | +10 ps extra path delay |
|---|---:|---:|---:|---|
| D4 V296 | 16.661 ps | 3483.339 ps | +0.4783% | Still above guard |
| D8 V296 | 9.643 ps | 3490.357 ps | +0.2763% | **Guard fails** |

The candidate fails the +50 ps setup guard under +20 ps additional critical-path delay at both depths. This is an additive-delay stress test, **not** a measured wire-length or process-voltage-temperature sensitivity.

## Finite-occupancy positive/no-win boundary

Use the independently checkable closed-loop model: `N` resident warps, `B` shared admission slots, Bernoulli readiness probability `q`, and `L` cycles between issues. A one-cycle operand-retiming penalty changes `L=1` to `L=2`. The exact stationary Markov law predicts `T(N,B,L,q)` admissions/cycle; an independently coded 160,000-cycle Monte Carlo simulation checks every regime within 0.012 admissions/cycle.

The necessary condition to offset this latency by frequency alone is `f_new/f_old >= T(N,B,1,q)/T(N,B,2,q)`. For `N=B=2`, the law simplifies exactly to `f_new/f_old >= 1+q`. Under the optimistic fixed-path D8 ceiling, this can hold only for `q <= 0.002763`; under D4, only for `q <= 0.004783`. Neither is a useful readiness regime for a high-utilization scheduler.

| Synthetic regime | N / B / q | Required frequency ratio | Best-case D4 L2/L1 work ratio | Best-case D8 L2/L1 work ratio |
|---|---|---:|---:|---:|
| Occupancy scarce | 2 / 2 / 0.90 | 1.9000 | 0.5288 | 0.5278 |
| Bandwidth saturated | 4 / 1 / 0.90 | 1.0009 | 1.0039 | 1.0019 |
| Balanced | 4 / 2 / 0.55 | 1.2868 | 0.7808 | 0.7793 |
| Sparse eligibility | 4 / 2 / 0.20 | 1.1818 | 0.8502 | 0.8485 |

The saturated synthetic regime has only a conditional **+0.39% D4 / +0.19% D8** best-case work-rate upside under this extrapolation, before any actual timing uncertainty, traffic, or power penalty. This is **not** a demonstrated GPU improvement. The hypothetical L1 reference is **not a measured feasible comparator**, and the real V296-versus-serial routed contestants both have the same added operand latency. Therefore this latency law must not be misrepresented as a direct V296-versus-serial benchmark.

## Equal-resource architectural consequence

At the frozen 30,000 µm² tile-slice ceiling, each completed routed contestant fits one slice: D4 V296, D4 serial, and D8 V296. The D8 serial integer capacity is **unknown** because the route timed out. Thus no additional complete physical slice has been demonstrated. Equal-clock, equal-latency bank-admission performance has not been shown to differ; an actual V296 throughput win requires a **feasible matched serial control** and measured or routed-justified frequency/occupancy/traffic differences. No power, production SRAM macro, or RTX-5090 equivalence claim follows.

## Reproduction and falsification

Run `python3 research/v296/v296_routed_clock_ceiling.py --self-test` and then `python3 research/v296/v296_routed_clock_ceiling.py`. The script recomputes exact Decimal timing limits, a stationary Markov admission model, independent seeded Monte Carlo, integer packing and additive delay stress. Local self-test passed. No prospective GPU holdout was opened.

**Next physical experiment:** diagnose the D8 serial route timeout from preserved logs/artifacts, then test a bounded symmetric repair that preserves depth, ports, 3.5 ns period and all physical constraints. Do not promote V296 until both matched controls pass extracted-RC setup, hold, electrical and DRC gates and a real workload advantage survives occupancy and bandwidth constraints. V296 remains the only provisional mechanism; V287 retired; Kernellum PR #119 and its holdouts untouched.
