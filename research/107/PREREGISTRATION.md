# Vektor-107 preregistration and provenance

Primary experiment preregistered before execution (2026-10-11):
P1: Cold fully associative cache with enough sectors produces the same compulsory misses for either grouping.
P2: At 32B sector granularity, 2-warp pitch-128 K=8 regrouping produces a smaller relative reduction than the 106 128B proxy.
P3: No-cache read misses equal read-sector requests; sufficient cache eliminates miss differences.
P4: Regrouping conserves per-lane memory event identity.

128 discovery cases (seed 1072026), 64 holdout (1079001), 24 minimally guided (1073333), 12.5% surprise share of primary 192 cases. Model: deterministic host-side SGEMM expressions, set-associative sector-LRU read cache, bypass writes. Not a GPU timing model.

Post-discovery H4 preregistered separately after observing seven group-major miss regressions. P5: step-major issue order has fewer miss regressions than group-major on new 96 paired configs (seed 1077707). Result 0 versus 5. This is post-discovery confirmation, not a predeclared primary result.

Full Python and independently implemented C++ models, raw configurations, results and SHA256 hashes are in the separately preserved Vektor-107 evidence package. This branch's compact executable checks the controls and paired confirmation.
