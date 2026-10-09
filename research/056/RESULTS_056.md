# Vektor-056: model-level results

The preregistered 96-configuration randomized holdout (2000 cycles/configuration) yielded +0.834% mean paired IPC for a static-uniform PTX proxy (configuration bootstrap 95%: +0.682% to +0.990%), versus +5.552% for an exaggerated high-alias control. All 96 zero-alias controls matched. Of 96 PTX-proxy pairs, 71 improved and 25 tied; all ties still saved RF transactions.

The exploratory **1,728-pair** grid (four seeds) had **30 PTX-proxy regressions**, all with two collector slots. Mean PTX-proxy gain was +0.821%. Independent replay matched 192 configurations with zero counter disagreements. A second compact model produced +0.837% mean on its own 96-probe sample.

These are synthetic software-model outcomes, not GPU benchmarks. The PTX proxy is NOT dynamically weighted. No 5090-class claim.

Next: dynamic compiled-kernel traces, dependency-aware banked RTL, mapped PPA.
