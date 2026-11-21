# V317 integrated issue-control: held-out placement-seed falsification (2026-11-02)

## Evidence and pre-registration
This result evaluates the *previously frozen* seeds 7, 19 and 37, not seeds chosen after seeing timing. Protocol: [FROZEN_INTEGRATED_PLACEMENT_SEED_CHALLENGE_20261102.md](FROZEN_INTEGRATED_PLACEMENT_SEED_CHALLENGE_20261102.md), frozen before [six-route OpenROAD run #41364018384](https://github.com/sushxnthd/vektor/actions/runs/41364018384) at source `0cd47389b11535917e2b89193d7520fe222501ba`. All six routes exited 0; the 698-file raw archive is [artifact 13107296352](https://github.com/sushxnthd/vektor/actions/runs/41364018384/artifacts/13107296352). An **independent raw-report parser** (not the original route scripts) ran in [audit #41372611335](https://github.com/sushxnthd/vektor/actions/runs/41372611335) and passed, preserving [artifact 13110320518](https://github.com/sushxnthd/vektor/actions/runs/41372611335/artifacts/13110320518). Checker: [audit_integrated_seed_challenge.py](rtl/audit_integrated_seed_challenge.py).

Pinned conditions: Nangate45 typical; ORFS `sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8`; 2.000 ns clock, 10 fF output loads, 120 x 120 um die, 112 x 112 um core, area-oriented ABC, timing-driven placement, 356 sequential cells, zero macros. Same 32-wave scheduler and grants, different bank-credit implementation. The 4096-cycle RTL comparison passed (13,153 accepted operations). The run has **no RF SRAM or GPU datapath**.

## Complete held-out outcomes

| Seed | Variant | Routed area (um2) | Fmax (MHz) | Setup slack (ps) | Setup violations | Hold slack (ps) | Power proxy (mW) | Wire (um) | Legal at 2 ns? |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 7 | source | 7426.72 | 499.235 | -3.063 | 1 | +5.425 | 5.49366 | 56442 | **NO** |
| 7 | pairwise | 6595.20 | 528.068 | +106.304 | 0 | +17.364 | 5.20472 | 52791 | **YES** |
| 19 | source | 7539.50 | 498.632 | -5.487 | 5 | +18.544 | 5.60451 | 57633 | **NO** |
| 19 | pairwise | 6577.12 | 518.366 | +70.861 | 0 | +16.731 | 5.18092 | 53984 | **YES** |
| 37 | source | 7367.67 | 499.111 | -3.561 | 6 | +17.454 | 5.46637 | 56757 | **NO** |
| 37 | pairwise | 6586.69 | 515.593 | +60.487 | 0 | +15.029 | 5.16356 | 53001 | **YES** |

Every row has **0 final routing DRC, 0 antenna net/pin, 0 hold, 0 max-cap, 0 max-slew and 0 max-fanout violations**, as independently checked. Setup failure disqualifies all three source seeds at the frozen 2 ns constraint; successful routing alone is not legality.

Paired-seed pairwise area reductions: **11.20%, 12.76%, 10.60%**. Paired Fmax advantages: **5.78%, 3.96%, 3.30%**. Default-activity power-proxy reductions: **5.26%, 7.56%, 5.54%**. These are three physical seeds, not three independent process corners or a statistical population estimate.

## Frozen-prediction adjudication and strongest control
- **P1 survives:** 3/3 pairwise seeds meet the complete reported 2 ns gate (threshold was >=2/3).
- **P2 survives:** pairwise area is lower in all three matched pairs.
- **P3 adversarial possibility not observed:** 0/3 source seeds close setup, despite source being only 3.06–5.49 ps late. This is not evidence that *no* legal source timing repair exists.
- **P4:** same-clock intrinsic scheduling service ratio remains exactly **1.000x**, because the compared RTL grants and port counts are equivalent.
- The strongest observed source by area is seed 37 (7367.67 um2), but it is timing-illegal. The strongest observed source by setup is seed 7 (-3.063 ps), also illegal. There is **no legal source** in this frozen three-seed set; it is therefore improper to describe a legal-source Pareto margin.

The ABC speed-mapped original was already falsified in [the previous control](RF_INTEGRATED_ABC_SPEED_FALSIFICATION_20261102.md) by setup, hold and capacitance failures. A *targeted, legal* source timing-repair search remains essential because a ~3 ps repair is small. Do not overinterpret seed luck as architectural necessity.

## Predictive tile-level boundary, not a GPU performance claim
For a source control period `T_s`, pairwise period `T_p`, and independently determined other-tile critical path `T_other`, integrated tile clock is `T_x=max(T_other,T_x_controller)`. A pairwise clock benefit is **zero** if `T_other >= T_s_controller`; it is partial if `T_p_controller < T_other < T_s_controller`, and potentially full only when `T_other <= T_p_controller`. The measured isolated controller timing is not a tile frequency.

Under a common demand ceiling `L`, shared bandwidth ceiling `C`, issue service `r` and total area budget `B`, the conditional throughput boundary remains

```
N_x = floor(B / (A_other + A_issue,x))
G = min(L, C, N_pairwise*r / max(T_other, T_pairwise))
    / min(L, C, N_source*r / max(T_other, T_source))
```

The result is **G=1** when both systems are bandwidth- or demand-saturated at the same common limit, or when area cannot purchase additional resources and another path dominates clock. No workload IPC, energy per instruction, or RTX 5090 equivalence follows from this test.

## Next kill gate
Run a **pre-registered, legal source repair** under identical area/clock/load/RC conditions (e.g. targeted timing-repair buffer sizing and source placement), retain every failure, and compare *best legal source* against best legal pairwise. Then transfer to multi-corner / wire-load sensitivity and SRAM+datapath-integrated timing, port traffic and activity-calibrated power. If a repaired source is competitive or the integrated tile is constrained elsewhere, reduce the claim to a local logic optimization or kill the architecture-level thesis. Keep this result and negative source seeds immutable.
