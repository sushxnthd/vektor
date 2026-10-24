# V296: prospective clock-skew and non-skew penalty falsification (2026-10-24)

**Evidence tier:** independently executable *analytical sensitivity*, anchored to the measured fourth-round high-RC extracted pre-CTS result, not a new physical experiment. The original six-case physical gate remains **FAILED**. V296 is the only active mechanism; V287 is retired. The workload holdouts remain **SEALED**. This note does not modify the preregistered four-way control-advantaged Pareto experiment.

## Why this is a necessary adversarial check

The fourth-round controls fail ideal-clock setup, but their positive extracted hold slack could, in an **optimistic single-effective-skew model**, be exchanged for setup slack. Calling those controls intrinsically timing-infeasible would be unjustified. Real clock-tree skew is path-specific and correlated, and neither a single idealized skew nor a clean timing budget repairs the one-hot control's 15 slew violations.

Reference from [completed run 40027903793](https://github.com/sushxnthd/vektor/actions/runs/40027903793), [artifact 12534554683](https://github.com/sushxnthd/vektor/actions/runs/40027903793/artifacts/12534554683):

| Controller | Extracted pre-CTS setup (ns) | Hold (ns) | Area (µm²) | Slew violations |
|---|---:|---:|---:|---:|
| Original | -0.113988 | +0.249579 | 7196.363949 | 0 |
| Optimized one-hot | -0.168119 | +0.270420 | 6949.250064 | 15 |
| V296 | +0.418903 | +0.282110 | 5987.926155 | 0 |

## Positive predictive boundary, with explicit assumptions

Let `s` and `h` denote measured pre-CTS setup and hold slack. Let `k` be a *single freely chosen* effective capture-minus-launch skew, `p_s >= 0` and `p_h >= 0` be non-skew setup/hold degradation from clock-tree insertion, parasitic changes, uncertainty and related implementation effects, and `g >= 0` be a desired setup **and** hold guardband. The toy model is:

```
setup_post = s + k - p_s
hold_post  = h - k - p_h

simultaneous guarded feasibility iff:
  g + p_s - s <= k <= h - p_h - g
or equivalently:
  p_s + p_h <= s + h - 2*g
```

The balanced skew is `(h - p_h - s + p_s)/2`, giving equal margins `(s+h-p_s-p_h)/2`. This is an **existential, optimistic timing-feasibility envelope**, not a guarantee that CTS can realize that skew across all setup/hold paths. A negative envelope rules out feasibility *within this toy model*, not in a physical flow that may resize, reroute or alter the paths. The formula does not model additional CTS area, clock power, skew topology, OCV, crosstalk or electrical repair.

### Frozen sensitivity regimes, before any CTS evidence

| Assumption | Original | One-hot | V296 |
|---|---:|---:|---:|
| Zero guardband and zero non-skew penalties | Optimistically feasible | Optimistically feasible | Optimistically feasible |
| 50 ps setup and hold guardband, zero penalties | Feasible in toy model | Feasible in toy model | Feasible in toy model |
| 50 ps guardband, 20 ps **each** setup/hold non-skew penalty | Infeasible in toy model | Infeasible in toy model | Feasible in toy model |
| 50 ps guardband, 100 ps **each** penalty | Infeasible in toy model | Infeasible in toy model | Feasible in toy model |

Under a 50 ps setup and hold guardband, the **combined non-skew penalty budgets** are **35.591 ps original**, **2.301 ps one-hot**, and **601.013 ps V296**. At zero penalty, the permitted effective-skew windows are respectively `[+163.988, +199.579] ps`, `[+218.119, +220.420] ps`, and `[-368.903, +232.110] ps`. Thus the one-hot control's guarded window is only **2.301 ps wide** even in this idealized model. The positive result is a timing-robustness *prediction*, not physical signoff.

### Adversarial control-favourable check

Hold V296 at its measured pre-CTS setup slack, but allow each control to consume hold slack until a 50 ps hold margin remains, with no non-skew penalties. The original could optimistically reach **+85.591 ps setup**, leaving V296 a **333.312 ps** setup lead. The one-hot could reach **+52.301 ps setup**, leaving V296 **366.602 ps** ahead. This model therefore predicts that *skew alone* does not erase the frozen +200 ps candidate setup advantage at this reference point, but other CTS penalties or independent control optimization can. It says nothing about candidate/control area changes or one-hot electrical closure.

## Next falsification, no retrospective tuning

1. Run an actual matched CTS/post-CTS timing, clock-area, slew, hold and extracted-RC experiment for all physically feasible contestants after the ongoing four-way experiment finishes. Preserve the existing four-way protocol and results unchanged.
2. Compare observed path-specific setup/hold changes against the above fixed 0/20/100 ps penalty scenarios and 50 ps guardband. Do **not** infer observed `k` from just one global worst setup/hold pair or claim that the effective skew is measurable as a single scalar across distinct paths.
3. If V296 fails real post-CTS setup/hold/electrical closure or loses the frozen resource/timing boundary to a fully closed control, retire it. Even if it passes, no same-clock issue-throughput gain is predicted and no tile-level or power claim is established.

**Reproduction:** `python3 research/v296/cts_skew_envelope.py --self-test` and `python3 research/v296/cts_skew_envelope.py`. Script uses only frozen measurements and no external packages; it reads no workload holdouts.
