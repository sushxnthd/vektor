# Vektor-105: Noisy address-hint anomaly (2026-10-11)

Evidence: synthetic memory-sector accounting only. No GPU speedup or physical claim.

The preregistered monotone-accuracy prediction failed. For a symmetric four-sector channel, a hint that always selects one of the three incorrect sectors is informative because it excludes the true sector. A 25%-correct hint is independent of the true sector.

Previously unseen 32-seed confirmation (sector incidences per instruction):
- q=0: mean 27.53125, range 26-29
- q=.25: mean 32, range 32-32
- q=.75: mean 30.90625, range 29-32
- q=1: mean 8, range 8-8
Path-only DWF baseline: 32.

Standard K-ary symmetric-channel identity: I(q)=log2(K)+q log2(q)+(1-q)log2((1-q)/(K-1)). At K=4, I(.25)=0; I(0)=log2(4/3). This is prior-art information theory, not a novel theorem.

Important limitation: the synthetic always-wrong hint generator knows the actual sector to exclude. That is an oracle and is not a practical predictor. The experiment falsifies raw classification accuracy as a sufficient proxy for coalescing quality; it does not establish a usable scheduling improvement.

Next: gather real Vortex/KPX compiler address-hint distributions and cross-warp legality traces, then evaluate independent timing with no future-address oracle. All RTX 5090-class gates remain inconclusive.
