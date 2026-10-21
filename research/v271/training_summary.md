# V271 training-only E1 sweep (seed 271001)
A deterministic software model completed 4 workload families x 4 service latencies x 7 allocation modes = 112 configurations. The committed CSV shows all modes at latency 30; the model generates all 112 raw records with --sweep. Unseen seeds 271901/271902/271903 remain unopened.

At 30-cycle service latency, alternating skew: hybrid mean request completion latency 32.1198 cycles vs best fixed 4+4 46.2662 cycles (30.58% lower), but fully shared 8-slot allocator 31.6772 cycles (1.40% lower than hybrid). Balanced: hybrid 31.9775 vs fixed44 31.8764 (0.32% worse). Single skew: hybrid 343.8003 vs fixed62 43.0086 (about 8x worse). Divergent: hybrid 31.9925 vs fixed44 33.8778, while fully shared 31.9662.

All modes use 8 logical MSHR credits. These are workload-model latencies, not measured throughput, energy, or electrical PPA. Positive law is CONDITIONAL on a physical area/timing advantage over fully shared; otherwise retire. The training profiles are synthetic burst streams and do not represent production GPU workloads.

Model assertions check capacity, class accounting, completion count and no drops. An independent RTL scoreboard is provided but has not run yet.