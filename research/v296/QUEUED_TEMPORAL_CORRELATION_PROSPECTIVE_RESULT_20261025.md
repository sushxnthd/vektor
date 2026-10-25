# V296: temporal hotspot persistence breaks static-bank throughput prediction (2026-10-25)

**Evidence tier:** Frozen, prospective **synthetic** queue replay with request-only pre-outcome diagnostic and two independent arbitration algorithms. **Not** a GPU trace, RTL simulation, integrated tile timing, or architectural speedup.

## Falsification and mechanism

The preceding exact independent-cycle law is not a throughput predictor for persistent queues. Fix 16 banks, four issue queues, two read ports/bank, FIFO depth 8, per-slot arrivals p=0.8 and conditional hotspot mass h=0.75. Every request reads one bank twice; the hidden bank hotspot persists from one cycle to the next with probability s, otherwise is redrawn uniformly.

All tested regimes have **identical unconditional uniform per-slot bank frequencies**, identical expected within-cycle collision probability c=h²+(1-h)²/15, and identical no-queue admission expectation q=1.758542. Temporal correlation changes FIFO head-of-line blocking, drops and offered-vs-served work.

Before any admission outcome, measure collision probabilities among raw incoming bank requests:

```
c = h² + (1-h)²/(B-1)
d = s*c + (1-s)/B
h_hat = [1+sqrt((B-1)*(B*c-1))]/B
s_hat = (d-1/B)/(c-1/B)
```

The first two equations hold for the frozen Markov latent-hotspot family. A seeded FIFO simulation at request-only inferred p,h,s then predicts admitted work. The strongest simple control runs **the same FIFO model and calibrated p,h**, but assumes independent hotspot redraws s=0. This is a simulation-based predictor, **not** a closed-form queue-throughput law or a general workload diagnostic.

## Prospective evaluation

The [preregistration](QUEUED_TEMPORAL_CORRELATION_PREREG_20261025.md) was committed at `e6e5601c` **before evaluation**. Code was committed separately at `7b0a61ff`. Frozen synthetic holdouts: s=0.35 and s=0.95. Each used 50,000 calibration arrival cycles (without admission outcomes), a disjoint 10,000-cycle warm-up, 80,000 measured evaluation cycles, and an independent 90,000-cycle prediction stream.

| Metric | s=0.35 holdout | s=0.95 holdout |
|---|---:|---:|
| Request-only estimated s | 0.348278 | 0.945004 |
| Estimated h | 0.749461 | 0.749723 |
| **Observed admitted/cycle** | **3.052300** | **1.906463** |
| Temporal FIFO prediction | 3.054800 | 1.938938 |
| IID-hotspot FIFO baseline | 3.162500 | 3.161150 |
| Old no-queue exact baseline | 1.760717 | 1.760051 |
| Temporal prediction absolute error | **0.002500** | **0.032475** |
| IID FIFO absolute error | 0.110200 | 1.254688 |
| Absolute-error reduction vs IID FIFO | **97.73%** | **97.41%** |
| Actual offered requests/cycle | 3.200450 | 3.194075 |
| Actual dropped requests/cycle | 0.148100 | 1.287613 |
| Actual average queued requests | 12.372788 | 21.510588 |
| V296/serial decision mismatches | **0** | **0** |

All preregistered gates passed on the local Python replay: absolute error <=0.08, >=50% reduction against the IID FIFO baseline, and zero mismatches. The full run checked queue conservation and <=2 reads per bank per cycle. Exhaustive priority equivalence also passed for all 81 two-bank/four-slot head states; three independent development replay tests passed. Results come from the script's frozen seeds, **not yet a hosted CI run** at the time of this report.

## Architectural consequence and negative result

At identical clocks, port resources, queue capacities and request streams, serial greedy and pairwise-priority implementations select the same requests on **every evaluated cycle**. The observed architectural admission-throughput advantage is therefore **exactly zero** in this matched-clock workload family. This cannot be turned into a V296 speedup claim. The candidate's existing controller area and extracted setup advantages survive only as *controller-level* physical observations. Their tile-level benefit remains conditional on integrated Fmax, memory traffic, overhead and area/power reinvestment.

Temporal persistence s is a missing predictor for queue-backed workloads. The measured synthetic throughput difference is a *workload sensitivity*, not a novel architecture mechanism. The exact static law is not mathematically false; applying it to queues was outside its assumptions. This experiment falsifies that **extrapolation**.

## Reproduce, limitations and next kill gate

```bash
python3 research/v296/queued_temporal_correlation.py --self-test
python3 research/v296/queued_temporal_correlation.py --evaluate
```

The hosted workflow is `.github/workflows/v296-queued-temporal-correlation.yml` and preserves raw JSON even if a frozen gate fails. This model omits memory latency, instruction dependencies, variable bank read counts, write ports, compiler mapping, real GPU traces, measured energy and integrated physical tile clocks. The pairwise implementation here is an independent **algorithmic** checker, not a new RTL-equivalence proof. Holdouts from other V296 protocols remain unopened.

**Decision:** Keep V296 provisional, V287 retired. Next substantive experiment must test a real/integrated tile or an equal-resource, measured-power control; further synthetic-law improvements alone do not establish a world-class architecture result. Kill any GPU speedup claim if integrated Fmax, bandwidth or overhead erases it. No RTX-5090 equivalence claim.
