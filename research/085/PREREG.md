# Vektor-085 frozen predictions and holdout protocol

Date 2026-10-10. Original preregistration is preserved in the full reproducibility package; this is a compact summary.

- P1 DISCRIMINATION: single-bank, uncached, 2-source + 1-destination instruction stream has shared p-port throughput <= p/3, and split read/write bound <= min(read_ports/2,write_ports). Confirmed within startup/drain residuals.
- P2 DISCRIMINATION: shared two read/write ports lose to split two-read/one-write on hot-bank workloads (not equal total ports). Confirmed.
- P3 CAPABILITY-BUILDING: value-aware RAW/WAW, cache invalidation, read/write arbitration match independent sequential architectural interpreter. Passed tested traces; not formally proven.
- P4 DISCRIMINATION: dependent chains are often scoreboard/latency limited. Supported in synthetic traces.
- P5 SURPRISE: holdout seeds 101 and 202; 32 initial minimally guided probes among 256 paired experiments.
- P6 EXPLOITATION: forecast read throttle with 4-cycle lookahead and threshold 2 improves selected spread anomaly by >=50% while preserving some wins. Initial selected trace passes, but generalization FALSIFIED: 17 wins,31 losses,48 ties across 96 unseen cases.
- P7 DISCRIMINATION: occupancy changes sign of shared/split reversal. Supported by 120-case phase grid; 60 no-cache cases 33 slower,10 faster,17 tied.
- P9 DISCRIMINATION: issue-time future writeback slot reservation eliminates WB queue stalls and improves selected 8-wave x128 spread by >=10%. Observed 490 -> 395 (19.4%).
- P10 EXPLOITATION: test generalization of reservation on 96 unseen cases; 47 wins,17 losses,32 ties, worst loss +113 cycles. Universal adoption REJECTED.

Frozen workloads: hot, spread, chain, reuse, matrix-token and mixed; 4 seeds (0-3) for controlled, unseen 101/202 for holdouts. Vary cache, latency, wave occupancy, bank count and collector slots. All results are software-simulated and assume uncosted cache updates and no physical timing.
