# FP32-PIPE-001

**Class:** CAPABILITY-BUILDING / DISCRIMINATION

## Mechanism
Replace the 556-bit exact-reference implementation as a production candidate with bounded-width staged arithmetic. The exact reference remains the correctness oracle.

## Preregistered prediction
A 24x24 significand-product front end should synthesize comfortably inside the same open Yosys flow that timed out on the wide exact oracle. Passing this test does not establish FMA correctness, frequency, area, or 5090-class throughput.

## Discriminator
1. Directed simulation must pass.
2. Generic Yosys synthesis must terminate under 180 s.
3. Record cell structure and compare against the exact-oracle timeout.
4. Only then extend with bounded alignment, signed add, normalization and one final RNE rounding.

## World-model update rules
- KNOWN if simulation + synthesis pass: bounded 24x24 product staging is viable in the current tool flow.
- FALSIFIED if synthesis times out: the bottleneck is not solely the 556-bit exact lattice.
- UNTESTED until subsequent stages: bit-exact fused semantics, 2.56 GHz, 128-lane scaling, PPA.

## Cheapest next discriminating experiment
Implement finite-path exponent alignment and a sticky-preserving bounded accumulator, then differential-test complete results against the existing >=10k fmaf oracle before scaling lane count.
