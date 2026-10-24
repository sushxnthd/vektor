# V296 parameter-scaling crossover: prospective area-law test (2026-10-24)

**Preregistered before the first synthesis sweep.** This experiment studies the **same sole active V296 pairwise two-read-port bank-admission mechanism**, not a new scheduler, bank architecture, or throughput optimization. V287 remains retired. The four-way high-RC physical run is independent and retains priority. This microbenchmark is *combinational arbiter area only*, not a GPU tile or physical-route result.

## Exact competitors and falsifier

Compare parameterized (i) V296 pairwise admission and (ii) serial decode-after-select 2-port one-hot occupancy, both with exactly S issue requests, two B-bit bank operands/request, 2 ports/bank, the same greedy request priority and no extra ports/state. Exclude scheduler and wave-index selectors from **both** area totals to isolate arbitration topology. Nangate45 Liberty, the same Yosys/ABC synthesis commands and same input/output widths must be used for every pair. An independent procedural port-counter oracle must match both RTL outputs on adversarial/random vectors; the smallest configuration additionally receives exhaustive input enumeration. Any mismatch invalidates the sweep.

## Frozen train/holdout split

Here B denotes *bank-index bits* and N=2^B denotes number of banks. The tuple is (B, S).

- **Fit only:** (2,2), (3,2), (3,4), (4,2), (4,4), (5,4), (5,8), (6,2), (6,4).
- **Unseen until fit is frozen:** (2,4), (3,8), (4,8), (5,2), (6,8).
- Synthesis must run all cases using the same scripts. The evaluator may read holdout areas only **after** it fits coefficients using the fixed training set; it must not refit on holdouts.
- The workload holdouts in `FROZEN_PREDICTIONS.json` remain **sealed**. These structural holdouts are distinct, public preregistered hardware-parameter configurations.

## Compact prospective boundary law

Define `X_pair = B * [4*C(S,2) + S]` as an operand-index comparator-bit proxy, and `X_mask = 2*S*2^B` as the one-hot mask-width proxy. Fit independent two-coefficient models on training data only:

`A_pair_hat = alpha_pair + beta_pair * X_pair`
`A_mask_hat = alpha_mask + beta_mask * X_mask`

Predict V296 area advantage iff `A_pair_hat < A_mask_hat`. Positive `beta` values are mandatory for a plausible monotone area law. Holdout pass requires both model MAPE <= 20%, both worst-case relative errors <= 30%, and >= 4/5 correctly predicted winner labels. If any criterion fails, **declare the simple crossover law falsified**; preserve all raw points and do not silently add features, tune split, or reclassify holdouts. Report actual area savings separately for each holdout, including negative results.

The law is a deliberately simple falsifiable hypothesis, not an asserted theorem. ABC sharing, comparator fanout, routing, physical buffering and scheduler/selector area can all invalidate it. Passing this gate would establish only an unseen *mapped combinational-area* prediction, not a physically validated GPU mechanism. A physically credible win still requires the independent four-way high-RC experiment, CTS, matched-resource control and tile/workload evidence.

## Evidence discipline

Record Yosys/ABC version, Liberty SHA-256, every synthesis log, and all RTL simulation logs. Fail closed on missing cases, invalid areas, failed oracle, or missing provenance. No claimed speedup, power reduction, memory traffic change, or RTX 5090 equivalence. Kernellum's independent research branch/PR must not be modified by this experiment.
