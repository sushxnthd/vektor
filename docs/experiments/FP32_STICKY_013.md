# FP32-STICKY-013 — pre-cancellation sticky compression falsifier

**Class:** DISCRIMINATION / SURPRISE

## Mechanism
Test the tempting bounded-FMA shortcut that compresses all low aligned bits into one sticky bit *before* an opposite-sign subtraction. This is not a production datapath; it is a negative-control architecture.

## Preregistered prediction
A single sticky bit is sufficient for final rounding after magnitude is known, but is not generally sufficient before cancellation: subtraction can expose discarded low-order structure. Therefore at least one deterministic finite FP32 counterexample should exist.

## Executable discriminator
`benchmarks/fp32_cancellation_probe.py` independently forms exact finite integer product/addend terms, applies a deliberately naive 52-bit pre-subtraction sticky compression, and searches 200,000 deterministic triples (seed `0x5090`). It fails if no counterexample is found.

## Decision rule
- Counterexample found: FALSIFY universal pre-cancellation sticky compression; preserve operand triple and residual.
- No counterexample: INCONCLUSIVE, not a proof; increase directed search/formalize.
- This test says nothing yet about a detector + correction path.

## World-model update on a counterexample
**FALSIFIED:** “all discarded low bits may be irreversibly collapsed to one sticky bit before opposite-sign cancellation” as a universal exact-FMA fast path.

**KNOWN:** the failure mechanism is information loss before subtraction, not the already-validated 24x24->48 multiplication.

**BELIEVED:** a practical bounded lane should retain a cancellation-safe window or detect risky exponent/sign geometry and recover through a slow exact/correction path.

**UNTESTED:** cheapest correct detector/correction boundary; complete bit-exact bounded FMA; timing/area/frequency.

## Cheapest next experiment
Sweep retained width and exponent delta on directed near-cancellation triples, cluster failures, then derive a detector predicate. Verify that predicate has zero false negatives against the exact oracle before RTL implementation.

No performance, area, power, frequency, or RTX 5090-class claim follows from this discriminator.
