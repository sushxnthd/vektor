# V297: persistent queues, temporal boundary, and first RTL synthesis gate (2026-10-29)

**Evidence tier: clocked RTL equivalence + generic logic synthesis + synthetic finite-queue workloads.** No matched standard-cell timing, extracted RC, electrical signoff, routed area, power, memory system, or real GPU throughput is available. V297 is the only active mechanism; V287/V296 remain retired. This report preserves all failures and adversarial controls.

## What changed
1. The persistent-queue protocol was frozen in commit `873b8054` before simulator/results. Three independent 64-entry queues consume the same immutable exogenous job stream, inspect only the oldest three requests, and share two issue slots and two read ports per bank. A 1000-cycle warmup precedes 20000 measurement cycles for four seeds. Unlike the prior open-loop experiment, bypassed requests remain queued, and the outcome is completed admissions, drops, and latency.
2. The first queue results were opened, then a **new** adversarial phase/offset protocol was frozen in `36cb558b`. Its results are exploratory/post-observation, not retroactively prospective. It tests three cyclic rotation phases, three motif offsets, and fresh seeds.
3. A **new** temporal-law protocol was frozen in `74b4b236` before evaluating eight new regimes. The law is proved under a first-order Markov assumption; non-Markov failures are retained.
4. Synthesizable RTL for V297 and rotating serial was committed in `1cc5604b`, with an independent Python trace oracle and clocked Verilog testbench. GitHub Actions run [40753159139](https://github.com/sushxnthd/vektor/actions/runs/40753159139) reported **17,832/17,832 matching sequential vectors**, including all 5,832 three-bank patterns/validity masks and 12,000 seeded full-bank patterns. Both parameterizations passed Yosys generic synthesis. The reported longest topological paths were **24** and **30** generic logic levels for V297 and rotating serial, respectively. These are **not** clock periods or routed critical paths; mapped standard-cell area and wire delays are unknown.

## Frozen finite-queue results

| Regime, arrivals/cycle | V297 completions/cycle | Cycle-rotating serial | V297 / serial | Drops V297 / serial | 99th latency V297 / serial |
|---|---:|---:|---:|---:|---:|
| Uniform16, 2 | 1.999900 | 1.998875 | 1.00051 | 0 / 0 | 3 / 14.5 |
| Three-job blocker motif, 2 | 1.500000 | 1.000000 | 1.50000 | 10001 / 20000 | 44 / 67 |
| Motif/uniform 37-cycle bursts, 2 | 1.698150 | 1.355763 | 1.25254 | 6037 / 12884 | 43 / 59 |
| All hot, 2 | 1.000000 | 1.000000 | 1.00000 | 20000 / 20000 | 64 / 67 |
| Motif, 1 | 1.000000 | 1.000000 | 1.00000 | 0 / 0 | 1 / 1 |
| Uniform16, 1 | 1.000000 | 1.000000 | 1.00000 | 0 / 0 | 1 / 1 |
| Motif, 3 | 1.000000 | 1.000000 | 1.00000 | 40000 / 40000 | 64 / 67 |

Values are means across four seeds; fractional drop/latency values are averages. Jobs arrive before service and overflow drops newest arrivals, which can alter the admitted bank-pattern distribution. This is a **finite synthetic queue**, not a realistic warp scheduler with scoreboard dependencies, cache misses, memory stalls, or occupancy.

**Crucial adverse control:** The deterministic three-job pattern can phase-lock with the cycle-rotating comparator. Against the best of three rotation phases on new seeds, V297's motif throughput advantage falls from 50% to **16.92–16.93%**, depending on motif offset; burst advantage remains **23.82–23.89%**. This is a post-observation adversarial robustness check, not an independent demonstration of novelty. The exhaustive maximal-admission oracle matches V297's motif throughput at approximately 1.5/cycle, showing that the win can be explained by ordinary feasible-pair selection. A physically matched optimal-subset selector remains unimplemented. The three-arrivals/cycle negative result shows that overload and drop ordering can eliminate the apparent win entirely.

## New compact temporal law and its precise boundary

Let M_t be the exogenous blocker-motif indicator, S_t the rescue indicator, and assume a stationary first-order Markov motif stream. With one-cycle cooldown, S_t=M_t(1-S_(t-1)). Write p=P(M_t=1), a=P(M_t=1|M_(t-1)=1). Since S_(t-1)=1 implies M_(t-1)=1, the Markov property yields E[M_t S_(t-1)]=a E[S]. Therefore

```
r = E[S] = p / (1 + a)
```

This exactly reduces to the previous iid law p/(1+p) when a=p. It is not a law of persistent-queue GPU throughput.

| Unseen regime | New Markov-law predicted rescues/cycle | Observed | Absolute error | Old iid-law error |
|---|---:|---:|---:|---:|
| IID 40% | 0.286419 | 0.286400 | 0.000019 | 0.000065 |
| Markov a≈0.9 | 0.261671 | 0.263655 | 0.001984 | 0.068242 |
| Bursts 11 | 0.262286 | 0.273088 | **0.010802 FAIL** | 0.060484 |
| Bursts 23 | 0.255898 | 0.261318 | **0.005419 FAIL** | 0.072225 |
| Bursts 53 | 0.252804 | 0.255240 | 0.002436 | 0.078377 |
| Bursts 101 | 0.251611 | 0.252928 | 0.001316 | 0.080631 |
| Uniform16 | 0.000927 | 0.000882 | 0.000045 | 0.000047 |
| Periodic 2-on/1-off | 0.444447 | 0.333635 | **0.110812 FAIL** | 0.066463 |

The preregistered 0.005 tolerance is met for the explicitly Markov and iid regimes, but **not** for short deterministic bursts or periodic two-on/one-off. Those streams violate the first-order Markov assumption; the counterexamples are not discarded. This is a useful exact modeling boundary, not a novel GPU architectural result.

## Conditional clock kill envelope

For the best rotation phase in the motif workload, V297 requires a candidate-to-control clock ratio above about **0.8552** to preserve its synthetic completion gain, assuming no latency/occupancy changes. For burst37, the conditional threshold is about **0.8077**. In uniform16, the margin is only **0.0513%** in throughput; tiny clock overhead can erase it. These thresholds cannot be extrapolated to a GPU tile or to a different workload mix.

## Next decisive experiment and kill rule

Use identical liberty, clock, placement, wire/load, and electrical constraints for V297 and the strongest rotating serial; include a *matched physical* maximal-pair selector or an explicitly justified equal-resource alternative. Validate timing, hold, capacitance, slew, routed area, and clock/power proxies. Then compare completion, tail starvation, and traffic on unseen non-contrived occupancy/memory-stall workloads. Retire V297 if no physically feasible gain remains or if the best simple control captures it. No additional speculative mechanism, no unsupported RTX-5090 equivalence.

Kernellum PR #119 and its prospective holdouts remain untouched.
