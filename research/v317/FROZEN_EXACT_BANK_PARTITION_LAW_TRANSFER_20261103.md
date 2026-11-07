# Frozen V317 exact bank-partition law transfer (2026-11-03)

This protocol is a follow-on to FROZEN_BANK_SCALING_CLOCK_ENVELOPE_20261103.md. The 8/16/24/32-bank sampled results are already known and are **training/exploration**, not prospective validation for this follow-on. Before evaluating any new holdout, a deterministic set-partition derivation found the exact iid-uniform-bank opportunity law:

P(E|B) = [153(B)_3 + 212(B)_4 + 61(B)_5 + 4(B)_6] / B^8,

where (B)_k is the falling factorial (zero for k>B). The model is exactly four valid ordered two-source requests, two read ports per bank, issue cap two, two cycles, head-preserving scheduling, and an oracle with complete batch lookahead. Its leading high-bank-count term is 4/B^2; the corresponding oracle/greedy *completion* ratio tends to 1 + 1/B^2. **This is an exact synthetic opportunity law, not a physically implementable GPU architecture.**

## Prospective holdout
- Unseen bank counts B=12,48,64, each with seeds 4111, 5113, 6113, 12,000 independent four-request vectors per seed.
- Independent implementation must not import the exact-law evaluator or the original scheduling evaluator. Enumerate legal head-preserving choices directly; compare oracle and greedy and verify opportunity gap is always 0 or 1.
- Independently enumerate all 3^8 and 4^8 labeled bank assignments and verify exact symbolic probability and expected greedy completions at B=3,4.
- Frozen prediction: for each new B, empirical event count must lie within five binomial standard deviations of exact symbolic E[N] (allow a floor of two events). This is a stochastic tolerance, not a claim of guaranteed agreement.
- Frozen win/no-win: under the conditional repeated-isolated-batch clock model with 0.5% added period, the **oracle** still wins at B=12 but loses at B=48,64. Shared bandwidth cap at 95% of baseline compute kills the gain for all B.
- The independent checker must reproduce the complete new seeded holdout and reject mutation of any result row.

## Interpretation and kill gates
A positive prospective transfer establishes a combinatorial boundary for a **clairvoyant synthetic ceiling**, not GPU IPC, real bank mappings, RF-cache misses, SRAM legality, area, power, routed timing, or sustainable queue performance. The existing V317 physical and electrical failures stay binding. Do not claim a 5090-class GPU or promote a new mechanism.
