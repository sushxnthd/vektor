# V294 retirement — equal-budget scheduling control (2026-10-23)

**Decision: RETIRE. Evidence: E1 directed RTL + generic synthesis, E0 independent software oracle. No characterized electrical STA.**

## Frozen directional holdouts
- Contended primary pair with disjoint alternative: primary-first two-choice control issues 3/4; V294 lookahead issues 4/4 (1.333x on this synthetic cycle).
- Conflict-free four disjoint pairs: 4/4 versus 4/4 (1.000x).
- Both passed the committed Icarus RTL testbench and independent Python oracle.

## Reproducible randomized workload model
2,000 independent four-scheduler synthetic request sets, eight hot banks, identical two-candidate metadata:
- Primary-first fallback: 7,190 grants total.
- V294 one-step lookahead: 7,392 grants total (+2.81% grant count).
- Exhaustive max-cardinality upper bound: 7,566 grants.
- V294 wins 236 cases, loses 40 cases, ties 1,724.
- These are grant counts, NOT instructions/second, energy, or GPU speedups.

## Matched generic synthesis
GitHub Actions run: https://github.com/sushxnthd/vektor/actions/runs/39886185175
Commit: 6c72b836f1f5f70a0ff251f27768ad78c936b408
Icarus directed holdouts, independent Python oracle, Yosys synthesis: PASS.
- LOOKAHEAD=0 control: **1,480 generic mapped cells**.
- LOOKAHEAD=1: **2,217 generic mapped cells**.
- Logic-count ratio: **1.498x**. No Liberty mapped area, max-cap/slew, fmax, power, or wire-load result.

## Decisive equal-resource falsifier
The proposed pressure scoring is itself an ordinary bank-pressure-aware greedy selector using the same two candidates and metadata. A pressure-aware greedy control with the same comparators and score policy is **functionally identical** to V294. The +2.81% is therefore only relative to a weaker primary-first control and cannot be called a distinct architectural improvement. The additional generic logic also violates a same-or-lower-area requirement against the simple control unless characterized physical evidence proves otherwise.

## Prior art
- Yamada et al., *Bank-Aware Instruction Scheduler for a Multibanked Register File*, IPSJ 2018, DOI 10.2197/ipsjjip.26.696.
- Gou and Gaydadjiev, *Addressing GPU On-Chip Shared Memory Bank Conflicts Using Elastic Pipeline*, IJPP 2013, DOI 10.1007/s10766-012-0201-1.
- GPU warp scheduling and bank-aware register arbitration are established; no novelty claim survives.

## Architecture consequence
Do not integrate V294. The current Vektor issue-control RTL remains unchanged. The result establishes a synthetic scheduling tradeoff, not a world-class GPU throughput law.
