# V149 SCIENCE ledger: bounded FP32 cancellation integration (2026-10-13)

Evidence class: RTL CANDIDATE; independent software oracle checked locally; HDL CI pending. This is GPU capability-building, NOT scientific novelty.

**Active question:** Can a bounded cancellation-only FMA path deliver bit-exact RNE with better matched-resource throughput/area/timing than a general finisher, without regressions on unseen workloads?

- **Frontier:** V148 integrated Wave32 exact 24x24 products but not FMA rounding. Earlier Vektor FP32-CLOSE-036 derived a 49-bit cancellation bound; V138's 556-bit exact reference is unsuitable for PPA. Specialized close/far paths are prior art.
- **Exact objective:** zero bit errors for accepted CLOSE cases, correct Wave32 tag/mask/backpressure, generic synthesis cell/depth proxy, later completed FP32 lanes/cycle per equal-resource area.
- **Strongest equal-resource baseline:** same V148 collector, multiplier, tags and RF ports, with a general FMA finisher replacing only the close stage. NOT YET IMPLEMENTED.
- **Mechanism:** opposite-sign terms with effective leading exponents within one bit have a 49-bit bounded exact difference. Prediction: close-path correctness across 3072 held-out real FP32 triples; lower PPA cost is untested.
- **Decisive falsification:** any supported result/flag mismatch, tag/mask corruption, width counterexample, or worse equal-resource throughput/PPA after adding far/special support.
- **Publishable threshold:** new mechanism beyond prior-art close-path specializations, independent replication and equal-resource Pareto improvement across unseen kernels. NOT MET.
- **Architecture-relevance threshold:** >=2000 real FP32 close cases bit-exact, full Wave32 stall tests, synthesis completes; eventual >=5% work/cycle or energy-proxy improvement with <=2% broad-workload regression.
- **Kill condition:** three runs without numerical coverage, PPA, or matched-resource kernel evidence: pivot to far/special finishing and full tile integration.
- **Wildcard:** later measure cancellation frequency on GEMM/reduction/divergent workloads; do not open unrelated research branches.

**Limitations:** RNE only, cancellation-only, NaN/Inf/zero-input cases not supported. out_supported=0 must never retire as a valid FP32 result. Generic synthesis is not silicon. No RTX 5090-class claim.
