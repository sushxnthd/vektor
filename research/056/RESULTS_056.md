# Vektor-056: model-level results

The 96-configuration randomized capacity-model holdout (2000 cycles/configuration) yielded +0.834% mean paired IPC for a static-uniform PTX proxy, compared with +5.552% for a deliberately high-alias control. All 96 zero-alias controls matched exactly. Of 96 PTX-proxy pairs, 71 improved and 25 tied. All ties still saved RF transactions.

The exploratory 864-pair grid had 20 PTX-proxy regressions, all with only two collector slots. A separate independently implemented replay matched 192 configurations without counter disagreements.

These are synthetic software-model outcomes, not GPU benchmarks or physical measurements. The PTX proxy is NOT dynamically weighted. No RTX 5090-class claim.

Next: dynamic compiled-kernel source traces and dependency-aware RTL plus mapped PPA.
