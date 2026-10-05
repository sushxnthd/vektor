# FP32-CANCEL-012 — cancellation-depth discriminator

**Class:** DISCRIMINATION / SURPRISE

## Mechanism under test
A bounded-width fused multiply-add datapath can lose correctness if it truncates the aligned product/addend before opposite-sign cancellation. The earlier 24x24 -> 48-bit exact product result does not resolve this risk.

## Preregistered prediction
If the product and addend have opposite signs and nearly equal magnitude, normalization can consume far more leading bits than a typical guard/round/sticky allowance. Therefore a production FMA must either retain sufficient cancellation headroom, use a provably safe sticky/jam scheme with recovery, or detect deep-cancellation cases and take a corrective path.

## Adversarial corpus
The next executable test must include exact 1*1 + (-1) cancellation, adjacent representable values around 1.0, normal/subnormal boundaries, exponent deltas spanning the finite FP32 range, and deterministic random finite triples. Results must be compared against the existing exact fused oracle, not host-language multiply-then-add.

## Competing explanations
1. A fixed bounded window is sufficient because exponent geometry bounds harmful cancellation after alignment.
2. Deep cancellation exists but a cheap detector plus slow correction path handles it without widening every lane.
3. The main cost is not cancellation width but special-case/rounding control.

## Decision rule
Do not freeze an alignment width from random-pass counts. Promote a width only after directed boundary tests plus bit-exact oracle comparison pass. Any mismatch is preserved with operands, exponent delta, sign pattern, cancellation depth and first differing output bit.

## Cheapest next discriminator
Implement two independently coded alignment/normalization candidates: (A) wide exact integer reference and (B) bounded shift-right-jam candidate. Sweep retained widths and detect the first mismatch boundary. If failures cluster only in deep opposite-sign cancellation, test a detector/correction architecture before globally widening the lane.

## World-model update
**KNOWN:** finite multiplication itself admits an exact 24-bit x 24-bit -> 48-bit significand representation before alignment.

**UNTESTED:** minimum safe bounded alignment/accumulation width for complete bit-exact FP32 FMA.

**BELIEVED:** cancellation, not multiplication, is now the highest-information arithmetic correctness target.

**FALSIFICATION condition:** any proposed bounded width that disagrees with the exact oracle on a directed or reproducible generated case is rejected as a universal fast path.

No frequency, area, power, throughput, or RTX 5090-class capability claim follows from this experiment design.
