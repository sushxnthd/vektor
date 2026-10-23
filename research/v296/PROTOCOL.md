# V296 — pairwise bank-collision admission (sole active kernel)

V295 is retired: the parallel one-hot predecoder cost 7,462.098 µm² against a 3,780.126 µm² matched control (Nangate45 mapped cell area). V287 remains retired. V296 is a **positive-law search**, not a continuation of V295's timing speculation.

1. **Bottleneck law:** Existing V-Tile arbitration materializes 16-bit bank occupancy masks for up to 8 register operands (4 issue slots × 2 reads). If the bank count B grows faster than concurrent operand count R, an equality graph over R operands may cost less than B-wide occupancy propagation. Hypothesized area crossover: A_pair≈a R(R−1) log₂(B)/2 versus A_mask≈b B R, with coefficients to be determined only after synthesis.
2. **Exact mechanism:** Compare the two bank indices of each candidate with bank indices of earlier accepted candidates; admit iff no bank exceeds two reads/cycle. Never change scheduler policy or read-port count.
3. **Strongest equal-resource controls:** Original V-Tile issue control AND optimized decode-after-select one-hot arbiter (V295 PREDECODE=0). Same 4 issue slots, 16 banks, 2 ports/bank, no new buffers, no new state.
4. **Win/loss boundary:** Pairwise wins only if characterized area ≤ min(control areas) and clean placed electrical timing improves. It should become less favorable when R is large relative to B; bank-conflict patterns must not alter accepted-wave decisions.
5. **Smallest RTL:** One pairwise-comparator arbiter plus identical scheduler and 4 bank-index selectors. No memory macros.
6. **Physical evidence:** 3-way RTL equivalence → Nangate45 characterized mapped area → OpenSTA with max-cap/slew and 0.5/1/2× wire/load sensitivity if area passes.
7. **Workload metric:** Accepted waves/cycle (must be identical); modeled instructions/sec under measured fmax, and modeled energy/area. Test compute, memory-bound and divergent regimes.
8. **Falsifier:** Functional mismatch, area exceeding best control, or no clean timing/energy benefit. Repair at most once.
9. **Frozen unseen predictions:** Compute-bound and issue-saturated should gain only if measured clean fmax increases; memory-return limited should show ≈1.000× gain if memory ceiling dominates. No holdout evaluation before physical gates.
10. **Architecture consequence:** Replace V-Tile RF admission logic only after matched-resource physical validation and independent checker. No RTX 5090 equivalence claim.

**Prior-art risk:** Pairwise hazard checking, scoreboard comparators and resource-conflict matrices are standard hardware techniques. A result can establish a Vektor-specific positive PPA boundary, not generic novelty.
