# V315 frozen capacity screen: positive resource law, zero incremental architecture novelty

**Decision: RETIRE V315 as a distinct architecture mechanism.** Frozen preregistration: [`81d9698`](https://github.com/sushxnthd/vektor/commit/81d9698ad7411abcacf0a0c51571f56d9b4ea7be). Independently hosted test: [Actions #41197545792](https://github.com/sushxnthd/vektor/actions/runs/41197545792), successful, including separate numerical-law and workload-demand audit. [Raw JSON and audit artifact](https://github.com/sushxnthd/vektor/actions/runs/41197545792/artifacts/13041014463).

## Frozen predictions and sampled results

100,000 jobs/phase; 2 phases/regime; two RF operands/instruction; 4 issue slots; hot bank has 2 read ports; 4 ALU ops/cycle. A fraction q of hot-bank reads can be replaced by one extra ALU operation. These are **optimistic resource-bound cycle counts, not measured execution cycles**.

| Regime | Mean hot-bank reads/inst per phase | Predicted dynamic / static | Observed dynamic / hindsight-optimal static | Incremental vs equal-information phase-aware compiler |
|---|---|---:|---:|---:|
| Frozen predicted win | 1.6 / 0.6 | 1.07448x | **1.07324x** | **1.00000x** |
| Frozen predicted no-win | 1.8 / 1.8 | 1.00016x | **0.99833x** | **1.00000x** |
| Prospective unseen transfer | 1.4 / 0.7 | 1.06115x | **1.05967x** | **1.00000x** |
| Adverse q=0.2, ALU cost=2 | 1.6 / 0.6 | 1.03825x | **1.03853x** | **1.00000x** |

All three preregistered prediction intervals passed. The hindsight-optimal static comparator is **stronger** than the frozen expected-static comparator. The candidate's 7.3% optimistic advantage in the win regime comes entirely from switching rematerialization fractions between phases. A compiler with the same phase labels and exactly the same available recomputation choices reproduces it without a new hardware mechanism. The required >=2% increment over that control fails identically.

## Derived predictive capacity boundary

Let d be hot-bank reads per instruction, q the exactly rematerializable share, f the selected share of eligible reads, c the extra ALU operations per recomputed operand, P hot-bank read ports, A ALU operations/cycle, W issue width. The optimistic resource envelope is:

```
lambda(d,f) = min(W, P/[d(1-q*f)], A/[1+c*d*q*f])
f_star(d)   = clip((A*d-P)/[q*d*(P*c+A)], 0, 1)
```

The checker independently searched a 1001-point f grid and agreed with the derived crossover within 0.002. The law predicts a **resource ceiling only**. It omits per-bank timing, data dependencies, cache hits, writes, register allocation, routing, control latency, rematerialization legality, ALU instruction semantics and actual GPU IPC. A true implementation can only do worse than this idealized bound.

## Prior art and research implication

RF caching and compiler-guided register-file transformations are already substantial research areas: [Malekeh](https://arxiv.org/abs/2310.17501), [LTRF](https://arxiv.org/abs/2010.09330), and [CORF](https://scispace.com/papers/corf-coalescing-operand-register-file-for-gpus-3ccibnpsjr). The screen does not establish a new architecture or a novel rematerialization algorithm. The equal-information comparator is decisive independent of those citations.

**Next work:** obtain real compiled operand-demand traces with physical-register and readiness semantics; benchmark against early-capable buffered collectors and existing RF reuse/cache mechanisms. Only promote a candidate that changes measured bottleneck capacity or demand **and** beats those strong controls. Do not claim a GPU speedup from these idealized numbers.

No RTL, standard-cell synthesis, placed/routed electrical evidence, power or integrated tile-level speedup is claimed.
