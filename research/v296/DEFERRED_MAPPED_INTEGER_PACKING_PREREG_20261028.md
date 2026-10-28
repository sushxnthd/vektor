# V296 deferred-write matched-area integer-packing falsification: frozen protocol (2026-10-28)

## Research question and provenance
At the frozen *mapped-only* D4/D8 areas of the symmetric deferred-write implementation, does the small V296-vs-strongest-serial area difference translate into even one additional whole tile slice at the 30,000 um2 physical area ceiling? At what larger *hypothetical replicated-slice* budget would an integer crossover first occur? This is an independent follow-on to the SHA-verified mapped synthesis audit; it does not change V296 or claim a routed win.

Fixed inputs (um2, from V296_DEFERRED_WRITE_MAPPED_TRANSFER_FALSIFICATION_20261028.md):
- D4: pairwise 13044.906, optimized serial 13510.406.
- D8: pairwise 18308.514, optimized serial 18769.492.
- Both: 16 banks, two reads per bank, one global write, four issue slots, identical deferred-write L=2 behavior. Serial remains V295 PREDECODE=0 with its fifth-stage physical optimization. V287 stays retired.
- No differential clock-frequency assumption. The 3.5 ns physical target is *not* asserted met. No wire, clock, SRAM macro, memory, power, or real GPU trace modeled.

## Frozen analytical predictions
Use exact integer micro-um2 arithmetic. At 30000 um2, both variants fit exactly one D4 or D8 slice, hence zero **capacity-derived** advantage at matched clock and equal admission semantics. For area a_c<a_s, the first k serial slices whose budget can fit k+1 candidate slices is k=ceil(a_c/(a_s-a_c)). Predict D4 k=29 (30 candidate) at 391801.774 um2; D8 k=40 (41 candidate) at 750779.680 um2. Independently scan all lower integer-count breakpoints and reject any earlier crossover. This is a *mapped-only* necessary, not physically sufficient, result.

## Frozen exploratory synthetic stress test
Use D8 first-crossover budget, exactly 410 resident warps, two-cycle per-wave cooldown, q=0.98 Bernoulli readiness per available wave, four issue slots, uniform 16-bank two-operand requests with 0.20 probability of copying first bank to second, and greedy two-port bank accounting. Compare 40 optimized-serial slices vs 41 pairwise slices; **the admission decision logic is deliberately identical**, because the verified V296/V295 controllers admit the same requests at equal ports. The sole model difference is mapped-area-driven integer slice count. Fixed seeds 20261028 and 20261029, 1000 warmup plus 7000 measured cycles per seed. All warps have deterministic paired per-cycle request streams, regardless of layout. Predict a positive unconstrained candidate gain (>0.5%) in both seeds, and zero useful throughput gain after an identical shared 100-wave/cycle cap (both must exceed 100). A separate 30000 um2 case with ten warps and one slice each must produce identical grant histories.

Check two independent integer-packing implementations, and a separate slow scheduler oracle on the first 32 cycles. Preserve any failed prediction; do not change seeds, workload, thresholds or model after opening outcomes. A pass is synthetic model evidence only, not hardware speedup.

## Kill criteria and limits
If at the actual 30000 um2 ceiling both mapped capacities are equal, there is **no capacity-based V296 gain** at equal clock. Even at a larger hypothetical crossover, a shared bandwidth cap can erase the extra slice. Any positive result requires physical feasibility of *both* same-depth contenders, an equal-resource tile-level accounting, and an actual throughput/clock boundary; the current pre-CTS experiment is still the next physical gate. Sealed real-workload holdouts remain unopened. No GPU/RTX-5090 equivalence claim.
