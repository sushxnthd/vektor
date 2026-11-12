# V309: prospective QV100 DRAM-latency sensitivity gate (2026-10-30)

## Scope and frozen design

This is a **qualification experiment, not a new GPU mechanism or architecture speedup**. Use the already-authenticated smallest original Rodinia 2.0-ft Pathfinder command list (4 kernel launches, 2 memory copies), the same source-pinned QV100-SASS simulator and the same trace/launch sequence. The baseline `-dram_latency 100` configuration is unmodified. Produce two copies of that exact config with **only** the active `-dram_latency` value changed to **200** and **400**. Record the complete source and variant SHA-256 digests. These three values were selected before examining perturbed outcomes.

Execute **two complete simulator runs per configuration**. Preserve raw logs and source configuration; use the independent per-kernel parser to require completion, sequential launch IDs, identical repeated counter vectors, positive cycles/instructions, and exact original launch count. Reject changed total instruction counts rather than treating them as speedup. Do not infer DRAM bytes from L1/L2 miss counts.

## Predictions and falsification

Predeclare the directional hypothesis: if this workload is meaningfully constrained by the modeled DRAM latency, raising the parameter to 200 and 400 should increase simulated cycles, and 400 should cost more than 200. If either latency increase produces **zero or fewer** cycles than baseline, reject a simple DRAM-latency-dominance claim for this workload. If 400 is not slower than 200, reject the monotone dose-response claim. A positive response is **not** proof of a memory bottleneck on physical V100 hardware; it is only a simulator-model sensitivity.

The frozen **predicted-sensitive regime** is the 400-latency counterfactual; the **predicted-small/no-claim regime** is the original 100-latency control. These are not architecture win/no-win workloads. No candidate architecture is promoted until an equal-resource, genuinely implementable alternative is specified and compared under physical timing/area constraints.

## Interpretation and next gate

Report total simulated cycles, percent cycle changes, L1D/L2 miss counters and repeatability. The strongest allowable conclusion is a causal response **within the simulator** to a single configuration parameter, not measured DRAM traffic, power, area or GPU speedup. If the response is small or inconsistent, prioritize issue/occupancy/port pressure rather than assuming a bandwidth-bound mechanism. If large, investigate DRAM service and concurrency with a second held-out workload before considering an architecture change.

Preserve failures and logs. Do not revive historical V287/V296, change Kernellum PR #119, or assert RTX 5090 equivalence. The active V309 branch and draft PR #26 remain the sole Vektor qualification workstream.
