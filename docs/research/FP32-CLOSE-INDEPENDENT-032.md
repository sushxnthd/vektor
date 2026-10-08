# FP32-CLOSE-INDEPENDENT-032 (2026-10-08)

Classification: CAPABILITY-BUILDING / DISCRIMINATION. Evidence: independent C++20 bitvector reference implementation, not RTL simulation or synthesis.

Preregistered prediction: the bounded CLOSE routing, alignment, magnitude, sign and zero results from prior 027/028/030 vectors should agree with a separately implemented model. A mismatch would falsify the claimed software-reference consistency. This does not establish RTL correctness.

Command: `g++ -std=c++20 -O2 -Wall -Wextra -pedantic fp32_close_independent.cpp -o fp32_close_independent && ./fp32_close_independent close_routing_vectors.txt close_vectors_adversarial.txt close_reachability_vectors.txt`

Results: 76,512 routing vectors (28,512 CLOSE), 25,762 adversarial cancellation vectors (all CLOSE), 6,241 reachable-boundary vectors (all CLOSE), total **108,515**, **zero mismatches**. Last set includes 3,120 product-shift=1 and one addend-shift=48 cases. The 027 and 028 vector suites do not cover product-shift=1.

Mechanism: independent C++ integer shifts, magnitude comparison and sign selection replicate the 49-bit RTL contract. No source-level RTL simulation occurred.

Residual: zero on these 108,515 deterministic reference vectors; RTL residual unmeasured. Competing explanation: both references may encode the same mistaken specification, so this is cross-implementation consistency rather than independent silicon evidence.

World model: KNOWN software-reference agreement and earlier inferred-latch synthesis failure; BELIEVED `sh=0` removes that latch; CONFLICTING no PPA data; FALSIFIED broad-coverage interpretation of the original shallow suite; ANOMALOUS product-shift=1 absent in 027/028; UNTESTED corrected RTL on adversarial vectors, synthesis, FAR integration, rounding, performance.

Cheapest decisive next action: commit `sh=0` latch correction, run the 108,515 vectors against the actual RTL and bounded Yosys, then synthesize equal-budget product-alignment alternatives. 5090-class gate remains INCONCLUSIVE.
