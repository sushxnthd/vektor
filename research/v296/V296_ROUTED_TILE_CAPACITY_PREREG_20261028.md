# V296 D4 routed-area tile-capacity falsification: frozen protocol (2026-10-28)

**Status:** preregistered before executing the new synthetic workload sweep. Sole active mechanism V296, V287 retired. This does not open any GPU workload holdout.

## Evidence and exclusion

Use routed area from GitHub Actions run [40646515864](https://github.com/sushxnthd/vektor/actions/runs/40646515864): D4 V296 19543.01964701699 um2; D4 strongest optimized serial 21914.943 um2. Crucially, the serial comparator FAILED routed setup and hold. Therefore **no pair of physically feasible architectures exists** at D4; all tile-packing comparisons in this experiment are **counterfactual sensitivity calculations, not feasible tile wins**. D8 serial remains censored and is excluded. The 30000 um2 frozen budget remains the real gate; 40000 um2 is a counterfactual sensitivity budget, not a retroactive replacement.

## Exact area boundary

At area budget A and per-slice overhead delta >=0, K_pair=floor(A/(19543.01964701699+delta)); K_serial=floor(A/21914.943). At A=40000, the nominal counts are 2 vs 1. The candidate loses its second slice if delta exceeds 40000/2 - 19543.01964701699 = 456.98035298301 um2 (2.338% per slice). At A=30000 both counts are 1. These are exact area arithmetic only, excluding inter-slice wiring, power distribution, memory, routing congestion and clocks.

## Frozen synthetic workload model

Independent candidate and serial arbitration implementations, 16 banks with two read ports each, four request slots per slice, eight resident waves/slice, L=2 cycles after issue, deterministic rotating wave selection and slice order, common global issue cap B, Bernoulli per-ready-wave readiness q and bank-zero hotspot probability h. Three seeds 3201/3209/3217, 12000 cycles each. Check 104976 small-bank canonical cases and enforce port invariants. Compare useful admissions/cycle, not performance in FLOPS. Frequency held equal, no memory or actual GPU traces.

Frozen regimes, in order:
1. **Conditional predicted win:** A=40000, B=8, q=1, h=0, ratio >1.5.
2. **Predicted no-win:** A=40000, B=1, q=1, h=0, exactly equal admitted waves/cycle despite extra nominal slice.
3. **Frozen-budget no-win:** A=30000, B=8, q=1, h=0, exactly equal.
4. **Fragility:** A=40000, B=8, q=1, h=0, +500 um2/slice removes candidate extra-slice capacity.
5. **Prospective mixed sensitivity:** A=40000, B=5, q=0.60, h=0.40; no fitted prediction, report raw ratio honestly. This is not a sealed real workload holdout.

A model ratio above 1 is **not** a demonstrated V296 benefit, because the serial control is infeasible, the tile budget was altered for sensitivity, and the model omits actual tile interconnect and memory. If all same-budget feasible comparisons have K_pair=K_serial, identical admissions and latency at equal clock imply no issue-throughput advantage. No energy, silicon, or RTX-5090 claim.

## Falsification and next gate

Preserve failures of the preregistered sign predictions. Do not advance a claimed tile-level win until the strongest serial comparator also passes extracted-RC setup, hold, cap/slew and DRC under matched conditions, and a complete tile (including overhead) exhibits measured throughput or energy advantage. The pending D8 serial routing run remains the priority. No architectural branch/PR replacement.