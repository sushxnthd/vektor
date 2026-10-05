# FP32-ACCUM-017 — bounded sign/magnitude accumulation gate

**Class:** DISCRIMINATION / CAPABILITY-BUILDING

## Mechanism
Test the next bounded FMA stage after exponent alignment: exact 56-bit sign/magnitude add/subtract with a 57-bit result. This isolates cancellation arithmetic from final normalization/RNE.

## Preregistered prediction
Given exact aligned operands, a 57-bit magnitude is sufficient for addition carry-out and subtraction is exact. Equal opposite-sign magnitudes must produce canonical +0 at this internal boundary.

## Adversarial cases
Maximum same-sign addition, one-ULP-like adjacent cancellation in both magnitude orders, exact cancellation, and 10,000 deterministic simulator-random tuples.

## Decision rule
Any mismatch falsifies this stage. A pass only validates bounded aligned accumulation; sticky semantics, normalization, RNE, IEEE special cases, timing, area and frequency remain unvalidated.

## Cheapest next discriminator
Compose MUL -> ALIGN -> ACCUM, preserve discarded-tail information explicitly, then compare normalization/RNE against the exact fused oracle with directed deep-cancellation vectors.
