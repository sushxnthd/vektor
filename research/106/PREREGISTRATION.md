# Vektor-106 preregistration (written before holdout execution)

Mechanism: source-visible 2D SGEMM row metadata can form persistent cross-warp
cohorts, reducing A loads and C-store 128-byte sectors at a migration cost.
Restricted to even W warps, pitch multiple of 32 floats, 128-byte sectors,
1 <= K <= 32.

Predictions for 112 independently seeded holdout configurations:
- sector savings = 2*W*(K+1);
- migrated lanes = 16*W;
- vecadd shows no reduction under its contiguous warp mapping;
- BFS indirect destinations lack exact affine hints; shared-target writes
  require a legality veto.

16 minimally theory-guided surprise configurations (12.5% of holdout+probe)
will break assumptions: odd W, nonaligned pitch, 64/256-byte sectors.
They test generalization, not a post-hoc fit.

Secondary prediction before 1,890 fixed-resource service-cost probes:
fewer sectors can lose when migration is costly. Compare
ceil(sectors/B)+ceil(moved/M)+setup under equal B,M,setup.
Asymptotic zero-setup break-even: M/B > 8/(K+1).
This is not a GPU cycle model.

Competing explanations: synthetic mapping; uncalibrated migration cost;
RF/cache/NoC pressure; hidden barrier/atomic/warp-intrinsic constraints.
Cheapest decisive experiment: actual Vortex simx memory traces and launch
mapping, then independent cycle timing and equal-resource comparisons.
