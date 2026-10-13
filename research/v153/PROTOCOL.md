# V153 protocol and evidence state

Base: V152 commit 83552c9147ff78c1f6df9b6f776e6ef0f357efae. V151 RTL unchanged.

Corpus: regenerate V150 oracle and V151 boundary corpus; record SHA256 of build/v151/full_vectors.txt. Expected count 24,220.

Differential RTL: compare two-stage V153 output and flags to V151 and frozen oracle. Check order, tags, masks and stalls; every input accepted once and retired once.

Synthesis: independently report generic cell count and longest path for V151 and V153 preparation and finish stages, with exact tool versions. Never equate generic cell count with silicon.

Physical follow-up: map to open liberty under identical constraints, match buffering and lane count, sweep dependent and independent compute, memory-stalled and divergent traces, report uncertainty and raw data.

Wildcard: vary dependency-chain depth and backpressure burst lengths for possible latency reversal. Prior art: standard pipelining and retiming. No novelty claim.

Current status: source prepared, GitHub Actions gate not yet verified.
