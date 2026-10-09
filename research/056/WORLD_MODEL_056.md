# Vektor-056 world model

KNOWN (software): zero-alias controls agree; fewer reads need not raise IPC.
BELIEVED: return bandwidth and collector occupancy dominate many regimes.
CONFLICTING: large synthetic alias gains versus low static PTX reuse.
FALSIFIED: dedup always improves IPC (20 exploratory regressions).
ANOMALOUS: all regressions occurred at two collector slots.
UNTESTED: dynamic physical aliases, RTL PPA, full GPU capability.

Prediction: PTX-proxy mean randomized gain <2%.
Observed: +0.834%; residual against threshold -1.166 percentage points.
Alternative: static PTX proxy misweights hot dynamic instructions.
Next: dynamic register-source traces and scoreboard-aware RTL.
