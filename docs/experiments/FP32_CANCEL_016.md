# FP32-CANCEL-016 — cancellation geometry CI gate

**Class:** DISCRIMINATION / CAPABILITY-BUILDING

## Mechanism

Promote the exact opposite-sign cancellation geometry probe into a reproducible gate before choosing a bounded FMA accumulator width.

## Preregistered prediction

Directed finite cases can cancel by at least 24 leading bits. Unguided random FP32 triples should make deep cancellation rare, so random traffic alone is not an adequate correctness test.

## Decision rule

A production bounded FMA must preserve enough low-order structure to survive adversarial cancellation. Do not infer a safe accumulator width from random-case frequency. The next implementation test must include directed cancellation and final RNE comparisons against the exact oracle.

## Evidence boundary

This experiment measures exact integer cancellation geometry only. It does not validate a complete FMA, timing, area, power, frequency, or RTX 5090-class capability.
