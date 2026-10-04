# FP32-MUL-CONTRACT-003

Classification: **DISCRIMINATION + CAPABILITY-BUILDING**

## Question
Before implementing bounded alignment/accumulation, is the 24x24 frontend representation itself exact for every finite FP32 encoding, including subnormals and signed zero?

## Mechanism
The RTL frontend represents a finite operand as sign, a <=24-bit integer significand, and an integer power-of-two exponent. Products therefore require only a 48-bit exact integer significand before alignment.

## Preregistered prediction
An independently written IEEE-754 decoder should reconstruct exactly the same rational value as `finite_exact_pair` for all sampled finite operands. Pairwise multiplication of the bounded tuples should equal exact rational multiplication with no rounding.

## Outcome
Independent local replication on **2026-10-04** passed:
- 200,000 finite FP32 encodings, deterministic seed `0x5090`;
- directed signed-zero, minimum/maximum subnormal, minimum normal, common normal, maximum finite and sign-boundary cases;
- 100,000 paired exact products.

Observed mismatches: **0**.

This is a software-model result, not RTL simulation or synthesis evidence. The repository checker is `experiments/fp32/check_mul_contract.py`.

## Residual and belief update
The finite decode/multiply representation is no longer the highest-risk part of ISSUE-FP32-002. The unresolved correctness risk moves to exponent alignment, cancellation normalization, single-round RNE packing, and special-case/flag handling.

World model:
- **KNOWN (software exact arithmetic):** 24-bit finite significands and 48-bit products are sufficient to represent the pre-alignment product exactly.
- **BELIEVED:** the existing bounded RTL multiply stage implements the same contract; its current directed RTL test is too small to upgrade this to a broad RTL claim.
- **FALSIFIED:** none in this experiment.
- **ANOMALOUS:** none observed in the deterministic sample.
- **UNTESTED:** complete bounded fused accumulation, bit-exact rounding, flags, multi-lane synthesis scaling and physical timing.

## Competing explanations / uncertainty
The checker shares the same high-level tuple convention as the model, so correlated specification mistakes remain possible. Exact rational reconstruction is independently coded, reducing but not eliminating that risk. Random sampling is not exhaustive over all 2^32 encodings.

## Cheapest next discriminating experiment
Generate tuple-stage expected outputs from the independent decoder and drive a large RTL vector test; then synthesize the bounded multiply stage under the same 180-second budget. Only after that should alignment/accumulation be promoted.

## Foothold status
No architectural performance foothold. This is a validated representation/capability foothold: it sharply narrows the correctness search space for the synthesizable FMA path.
