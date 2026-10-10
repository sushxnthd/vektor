# Vektor-088: deadline-class writeback starvation and triggered protection

2026-10-10. Base: Vektor-087 b1776681fd623da20c26279a6f8bed22577f2843. **Simulation only; no GPU performance claim.**

## Preregistered mechanism
Vektor-087 rotates fairness pointers separately for each latency. Earlier, long-latency reservations can claim future bank-write slots before shorter-latency requests have an opportunity. Hypothesis: protecting selected absolute completion deadlines prevents cross-latency starvation; triggering protection only after a class waits 16 cycles preserves more admission capacity than protecting every deadline. Negative prediction: correlated bursts can waste reserved slots.

## Results
On 4 continuously requesting clients with latencies 1,2,3,4, 1 bank/1 write port, 4096 admission cycles:
- Vektor-087 baseline: [1,1,1,4096] grants; 4099 total.
- Fixed deadline-class owner: [1025,1025,1025,1024]; 4099 total.
- Starvation-triggered deadline protection: [205,205,205,3484]; 4099 total.
These are admissions for future completions; totals may exceed elapsed cycles at the observation boundary. They are **not executed instructions**.

Across 168 configurations including 21 minimally guided probes (12.5%): triggered vs baseline total admissions 0 wins, 154 ties, 14 losses; mean relative difference -0.264%. Static protection 0 wins, 57 ties, 111 losses; mean relative difference -16.60%. Correlated-burst negative result: triggered 3150 vs baseline 3306 (-4.72%). No throughput dominance.

Independent C++17 vs Python: 128 configurations x 256 cycles x 3 policies x 2 observables = **196,608 exact grant-mask/due-count checks matched** in the full reproducibility package. 20 Python tests passed (8 inherited). RTL is proposed but **not yet verified or synthesized**.

## World model / Discovery Protocol V2
- KNOWN (simulation): per-latency RR does not imply global cross-latency fairness.
- KNOWN (simulation): triggered protection restores progress to continuously requesting shorter-latency classes in the tested model.
- BELIEVED: class-level starvation-triggered protection merits RTL feasibility testing.
- CONFLICTING: stronger equity versus lower admission capacity on correlated workloads.
- FALSIFIED: unconditional protection is free; triggered protection always matches baseline throughput.
- ANOMALOUS: admission losses depend on burst phase and deadline alignment.
- UNTESTED: reset, cancellation, tags, coherent register values, per-warp liveness, PPA, compiler traces, GPU integration.

Prediction residual: saturated mixed demand matched the predicted direction, but trigger A=16 yielded only 205 admissions per starved class (5.0% share), not equitable distribution. Random independent demand matched baseline admissions in the selected seed; correlated bursts falsified universal zero-cost protection.

Competing explanations: finite-horizon startup effects and admission-versus-retirement accounting. Uncertainty: no real instruction dependencies, backpressure, queue limits or cancellation.

## Novelty and next action
Reservation calendars, RR fairness and GPU writeback bank-conflict mitigation are prior art. See Gou & Gaydadjiev (2013), DOI 10.1007/s10766-012-0201-1; Sadrosadati et al. (2020), arXiv:2010.09330; Liu et al. (2026), arXiv:2608.19628. **No novel algorithm is claimed.**

Next decisive action: RTL/Python trace equivalence and bounded safety proof of the triggered controller, then cancellation/generation tags and integration into coherent V-Tile simulator. All RTX 5090-class gates remain INCONCLUSIVE.

Run the compact regression: `python3 experiments/wb_age_guard_088.py`.
