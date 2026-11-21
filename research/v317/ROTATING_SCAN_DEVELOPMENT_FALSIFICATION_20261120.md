# V317 rotating-scan development falsification — 2026-11-20 UTC

The preregistered one-bit rotating scan candidate was implemented in `rtl/rotating_scan_prospective_20261120.py`. The 4 development seeds (20261121–20261124) were run locally against compact scan-order greedy using the same generated arrivals for each pair, 20,000 cycles, 2,000 warmup, three bank regimes, four fixed arrival rates plus Markov burst traffic (60 paired cells).

Local development execution: `python rotating_scan_prospective_20261120.py --short` returned `n=60`, geometric mean candidate/compact throughput `0.999934767939798`, minimum cell ratio `0.9983679686649983`, maximum cell ratio `1.001493103284827`. These figures are from a locally executed copy of the submitted source; a byte-identical GitHub checkout or hosted CI execution is not yet confirmed. The simulator asserts per-cycle conservation, FIFO capacity, bank-port feasibility, oldest request grant, and no duplicate grants. It does **not** implement an independent checker or RTL.

**Decision: kill the rotating-scan candidate at the development gate.** No development cell approaches 1.02x; the candidate's one-bit state and scan mux would only add physical overhead. Do not open the reserved 16 holdout seeds, tune against them, or initiate RTL/physical promotion. The holdout remains unobserved. This is a negative result on a synthetic four-slot tile arbitration model, not a GPU IPC or RTX 5090 result.

Prior protected-oracle prospective falsification, area dominance of compact greedy, and illegal routes remain binding. V296/V317 is current; V287 historical. Keep exactly one active candidate (now rejected) and PR #34. Future science requires a separately justified, preregistered mechanism rather than post-hoc retuning of this one.
