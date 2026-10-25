# V296: latent within-cycle hotspot falsifies marginal-bank sufficiency (2026-10-25)

**Evidence tier: exact finite-sample expectation + independent concrete-bank enumeration + frozen, prospective synthetic evaluation. Not a measured GPU trace or architecture speedup.**

## Decision
A marginal per-bank frequency histogram and within-request operand overlap **do not suffice** to predict bank admissions. Even when every slot has exactly uniform bank marginals and the same A=B operand overlap, an unobserved cycle-level hotspot creates cross-slot dependence and can sharply reduce admissions. A preregistered request-only diagnostic successfully predicts two held-out synthetic regimes. The result is an identifiability and workload-model finding, **not** new GPU architecture or a V296 speedup. V296 remains sole provisional mechanism; V287 stays retired.

The protocol was committed first at `8aa6200`, before executable evaluation or results: [frozen preregistration](LATENT_HOTSPOT_PROSPECTIVE_PREREG_20261025.md). No existing prospective GPU holdouts were opened.

## Mechanism and predictive boundary
16 banks, four ordered issue slots, two read ports/bank, each valid independently with probability p=0.8. A hidden bank H is uniform per cycle. Conditional on H, each slot uses H with probability h and distributes remaining mass uniformly over the other 15 banks. Each request uses two reads of the chosen bank (A=B), so at most one request can be admitted per bank per cycle.

Despite a varying latent hotspot, **every slot's unconditional bank probability is exactly 1/16**, and same-bank operand overlap is 100% for every h. The exact expected admissions are

```
q(h) = 1 - (1 - p*h)^S + (B-1) * [1 - (1 - p*(1-h)/(B-1))^S].
q_uniform = B * [1 - (1 - p/B)^S].
```

A request-only, pre-outcome statistic is the collision probability c between two valid slots in the same cycle:

```
c = h^2 + (1-h)^2/(B-1).
h_hat = [1 + sqrt((B-1)*(B*c-1))]/B, for h >= 1/B.
```

This statistic identifies h **only within the preregistered one-hot latent-hotspot family**; it is not a universal GPU trace predictor. At equal clock and resources, V296 and serial one-hot admit the **same requests**, so architectural throughput gain from this law alone is exactly zero.

## Frozen development sweep

| Conditional hotspot mass h | Exact admissions/cycle | Uniform-marginal baseline | Baseline overprediction relative to truth |
|---:|---:|---:|---:|
| 1/16 | 2.967900 | 2.967900 | 0% |
| 1/4 | 2.850202 | 2.967900 | 4.13% |
| 1/2 | 2.407530 | 2.967900 | 23.28% |
| 3/4 | 1.758542 | 2.967900 | 68.77% |
| 1 | 0.998400 | 2.967900 | 197.27% |

This is an exact counterexample to the sufficiency of aggregate marginal bank histograms even when operand overlap is fixed. It is *not* evidence that real workloads exhibit this distribution.

## Frozen prospective synthetic holdouts
The independent simulator used 40,000 **calibration** cycles per regime to estimate within-cycle request collision and h, then evaluated predictions on **80,000 disjoint cycles**. Seeds, splits and absolute-error threshold 0.05 were frozen before execution. No admission outcomes from calibration were used to estimate h.

| Hidden h (unseen) | Request-only h estimate | Prospective q prediction | Independent oracle observed q | Abs error | Uniform baseline abs error |
|---:|---:|---:|---:|---:|---:|
| 3/8 | 0.373905 | 2.664064 | 2.657988 | **0.006076** | 0.309913 |
| 5/8 | 0.624238 | 2.103966 | 2.104500 | **0.000534** | 0.863400 |

Both pass the frozen 0.05 threshold. Independent concrete-bank exhaustive enumeration matched the exact law for four small configurations. Additional self-tests cover parameter inversion, limiting cases and invalid inputs. Evaluation marginal bank frequencies remained within 0.00128 of 1/16 per bank (max absolute deviation).

**Reproducible hosted PASS:** [GitHub Actions run 40150487736](https://github.com/sushxnthd/vektor/actions/runs/40150487736), with archived validation log. Execute `python3 research/v296/latent_hotspot_identifiability.py --self-test`.

## Physical/tile consequences and limits
This corrects a dangerous workload-level assumption: per-bank frequency counters alone may hide burst-local contention. A controller's measured physical timing advantage cannot be multiplied by the IID model's admissions when the workload has latent per-cycle concentration. A pre-outcome within-cycle collision statistic is required for this particular family.

Cross-**cycle** correlation by itself does not alter expected admissions when each cycle starts with empty bank usage and its within-cycle joint law is fixed. Persistent scheduling queues, bank state, memory feedback and correlations among requests can violate these assumptions. No GPU trace, queueing system, memory traffic, physical power, equal-area tile clock or tile throughput was measured here.

Next decisive falsifiers: request-only prediction on *actual*, held-out trace segments with independent replay, plus matched equal-resource tile timing/power; retain a strong empirical baseline and reject claims that do not transfer. No RTX-5090 equivalence claim.