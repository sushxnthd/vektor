# Vektor-109: cohort conservation

The previous V108 checker only verified dependency and epoch ordering. It did not enforce event conservation or the Wave32 single-instruction cohort interface. V109 adds a strict validator, independent C++ implementation and source-trace schema audit.

Run repository smoke test with Python 3 and g++:

    python3 research/109/quickcheck.py

This executes 648 independent Python/C++ comparisons. The full preregistered 2,564-case study (including the original V108 model, holdout data, test harness and SHA256 manifest) is in the Vektor-109 reproducibility archive.

External trace baseline: Vortex SimX at commit 7fe19369587c087f902c3e2bc2add612aa910a95. The official trace CSV omits per-lane effective addresses, so actual coalescing comparisons remain blocked pending LSU instrumentation.

All performance and physical-feasibility gates remain INCONCLUSIVE.
