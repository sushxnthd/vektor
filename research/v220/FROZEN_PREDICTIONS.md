# V220 — stream-hinted L1 bypass: prospective boundary test

Evidence class: analytical / software model only; not an architecture claim.

## Mechanism (one only)
Do not allocate a cache line on a read miss explicitly labeled streaming. Retain normal demand fills for non-streaming accesses. Cache capacity, ways, read bandwidth, and memory bandwidth are unchanged. Prior art includes stream bypass and insertion policies; novelty is **not** claimed.

## Derived boundary
Let H be distinct frequently reused lines mapping to one cache set and C the set's capacity. If H < C, a well-tuned SRRIP/BIP control can retain all H lines and stream bypass may have zero benefit. If H = C, even a distant-insertion control must evict at least one hot line to admit a unique stream line, so bypass can preserve hot lines. A gain requires memory bandwidth to limit execution and the control to admit some one-touch lines.

For miss rate m and available cache-line memory bandwidth b (lines/request-cycle), idealized throughput upper bound X <= min(1, b/m). This is a throughput **upper bound**, not a cycle-accurate model.

## Original frozen holdouts — cannot change
- positive: seed 9173, H=15, S=4 streams per hot access, C=16. Predicted >=1% modeled gain. **Failed: 0%.**
- negative: seed 9917, H=8, S=0, C=16. Predicted 0%. **Passed: 0%.**

## NEW prospective boundary holdouts — freeze before execution
- positive boundary: seed 12031, H=16, S=2, C=16, 130 rounds, divergent hot order, bandwidth 0.12 lines/cycle; predict >=1% modeled gain against best of SRRIP and BIP.
- negative boundary: seed 12037, H=8, S=0, C=16, 130 rounds, compute hot order, bandwidth 0.12 lines/cycle; predict exactly 0% gain.

## Physical gate
Functional equivalence of cache contents for nonstream accesses -> RTL simulation -> synthesis -> mapped electrical checks -> matched timing/area -> modeled traffic/throughput -> wire/load sensitivity. Any unexecuted stage blocks architecture qualification. Stronger control: hint-aware bypass with same admission bit (identical mechanism); this makes breakthrough novelty untenable unless a distinct advantage is found.

## Falsification
If the strongest simpler hint-aware bypass matches candidate (expected), retire V220 as a breakthrough even if it beats SRRIP/BIP. No integrated tile change before full physical qualification.

## V153/V156
FP32 cutset/arrival remains retired and electrically unqualified. No symbolic headroom claims.
