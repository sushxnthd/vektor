# Vektor-099 CI evidence — 2026-10-11

Tested commit: `b3000605e1b181ad70f36c407b1581c7a95999d1`.
Workflow: https://github.com/sushxnthd/vektor/actions/runs/38105566692
Both jobs PASSED on GitHub Actions Ubuntu runner.

## Claim -> implementation -> experiment -> measurement

Claim: V094 implements FINAL-wins on simultaneous cancellation and FINAL;
V099 implements cancel-wins. Implementation: V099 masks `cb_live_match`
with `!cancel_mask[cb_tag]`, preserving tag retirement.

- Python exhaustive one-tag Boolean oracle: 64 states, V094 one cancel-wins
  counterexample, V099 zero. Independent C++ replication matched.
- Icarus RTL directed testbench: 5/5 checks passed, including explicit V094
  negative control, ordinary FINAL, reset priority, nonfinal and later FINAL.
- Yosys generic cell synthesis, equal parameterization:

| TAG_BITS | V094 cells | V099 cells | Difference | Relative increase |
| --- | ---: | ---: | ---: | ---: |
| 1 | 53 | 55 | +2 | 3.77% |
| 2 | 112 | 116 | +4 | 3.57% |
| 3 | 279 | 289 | +10 | 3.58% |
| 4 | 603 | 619 | +16 | 2.65% |

These are **generic logic cell counts**, not placed area, frequency, power,
timing closure, or silicon measurements. The 8 syntheses are not equal-PPA
comparisons. No GPU performance gate advanced.

Prediction residual: zero for the preregistered Boolean policy difference.
Hardware cost was not preregistered; report it as exploratory. Relative
cell-count increase is small but cannot establish PPA acceptability.

Competing explanation: V094 may be correct if FINAL-wins is the intended
architectural cancellation policy. This is conditional contract
discrimination, not a universal V094 bug or an architectural novelty claim.

World model update: KNOWN=RTL simulation confirms policy distinction and
Yosys successfully synthesizes both designs. BELIEVED=explicit cancel-wins
is preferable for user-observable cancellation. CONFLICTING=FINAL-wins
remains a coherent alternative. FALSIFIED=V094 cancel-wins. ANOMALOUS=none
in directed tests. UNTESTED=sequential formal equivalence, V098 composed
integration, source quiescence, physical PPA, 5090-class performance.

**Single next decisive action:** compose V099 with the V098 return fabric,
test simultaneous cancel/FINAL under adversarial multi-producer backpressure,
then formally verify transaction conservation and tag-incarnation safety.
