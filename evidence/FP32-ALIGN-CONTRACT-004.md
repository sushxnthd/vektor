# FP32-ALIGN-CONTRACT-004 — exact alignment budget discriminator

**Class:** DISCRIMINATION / CAPABILITY-BUILDING  
**Parent evidence:** FP32-MUL-CONTRACT-003  
**Status:** preregistered; implementation pending CI.

## Mechanism under test
For finite binary32 FMA, multiplication produces an exact 48-bit significand. Before signed addition of c, the smaller term need not retain an unbounded right-shift tail: a bounded alignment representation carrying retained magnitude plus guard/round/sticky (GRS) information should be sufficient for final round-to-nearest-even, provided cancellation-sensitive cases retain enough leading precision.

## Competing hypotheses
- H1: a fixed bounded accumulator with explicit sticky compression can reproduce the exact oracle for all finite operands.
- H2: cancellation after opposite-sign alignment creates cases where an aggressively truncated GRS-only representation loses information; extra low-order carry/cancellation bits are required.

## Preregistered prediction
Random ordinary cases will make both designs look correct. Discriminating cases cluster where signs oppose and product/c exponents nearly coincide, or where the discarded tail lies at a halfway boundary. Therefore validation MUST oversample:
1. exponent deltas 0..8 with opposite signs;
2. exact/near cancellation;
3. normal/subnormal boundary;
4. halfway-even and halfway-odd rounding;
5. very large exponent deltas to test sticky saturation.

A candidate is not accepted from random testing alone.

## Measurement
Compare candidate finite-path result bit-for-bit against the existing exact FMA oracle. Report mismatch count by exponent delta, sign relation, cancellation depth and result class. Preserve the first counterexample for every mismatch cluster.

## Decision
PASS only after directed boundary corpus + >=100k deterministic random finite triples show zero mismatches, followed by RTL equivalence on the same tuple contract. Any mismatch falsifies the tested width/compression rule, not IEEE-754 or the golden oracle.

## Cheapest next experiment
Implement two Python models sharing the exact 48-bit product:
A. deliberately aggressive GRS truncation;
B. wider cancellation-safe accumulator.
Anomaly-mine disagreement regions before committing RTL width.

## World-model update
KNOWN: 24x24 -> 48-bit product is exact for finite binary32 inputs (FP32-MUL-CONTRACT-003).
BELIEVED: bounded alignment is feasible.
UNTESTED: minimum cancellation-safe width and compression rule.
FALSIFIED: scaling the 556-bit exact oracle directly as the production lane.
