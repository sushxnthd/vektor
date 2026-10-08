# FP32-RNE-CONTRACT-035 (2026-10-08)

Evidence class: SOFTWARE MODEL, not RTL/silicon. On isolated branch research/fp32-close-gate-035.

DISCRIMINATION: Independent exact ordered-FP32 binary search versus bit-width-aware Python translation of RTL round-to-nearest-even packer. Preregistered prediction: zero disagreements across randomized/boundary/midpoint cases.

Outcome: 90,945 distinct dyadic inputs (65,000 random; 945 boundary; 25,000 midpoint); zero result/overflow/underflow/inexact mismatches, tie compared only when nonoverflow. 20,010 accepted vectors from prior FP32-CLOSE-RNE-034 independently replayed, zero disagreements. New standalone oracle corpus: 65,945 vectors, SHA-256 3c00410d0b406aef473748879415c449fabcd59ef033ffc5f30b404d8c446238, not executed on RTL.

Negative result: initial instrumentation reused the 'tie' counter for both input category and output flag, inflating apparent sample count to 117,026; corrected and rerun, true count 90,945.

KNOWN: GitHub Actions run 37737329904 passed 20,000 cancellation vectors but Yosys failed due inferred latch in temporary sh. BELIEVED: default sh=0 in always_comb removes latch. FALSIFIED: 117,026 distinct tests claim. UNTESTED: corrected RTL simulation, RNE synthesis, timing/area/power, broad RTX 5090-class gates. ANOMALOUS: overflow may assert internal GRS tie diagnostic, which is not IEEE exception.

Next decisive action: apply one-line sh default on research branch; run existing CLOSE gate, then 65,945-vector RNE contract gate, preserve CI logs, compare equal-budget generic vs specialized aligners. No novel hardware claim or 5090-class equivalence.
