# Vektor-063: return-lane contention and ACK packing

Status: software-model foothold, RTL execution pending. Research class: DISCRIMINATION / EXPLOITATION / CAPABILITY-BUILDING.

Vektor-062's strong quiescence ACK was assumed to use an independent return path. Charging ACKs to the same one-flit/cycle link as data changes the no-replay capacity ceiling from about 1.0 to 0.5 transactions/cycle. Packing up to four ACK tags into one fixed-width flit can raise the shared-link ceiling to 0.8.

Reproducible synthetic outcomes at 64 tags, no replay, 16,000 cycles: independent ACK 0.999750, shared unbatched ACK 0.499958, shared batch4 ACK 0.799896 transactions/cycle. Packing improves modeled throughput 60.0% relative to unbatched shared return. Negative result: at two tags batching regresses 1.63% due to delayed tag reclamation.

144 structured software simulations, 18 minimally guided probes, 18 holdout checks, 128 independent C++/Python comparisons. Synthesizable arbitration RTL, testbench, and GitHub Actions workflow are committed but no successful RTL run is confirmed. Strong fabric quiescence and ACK packing physical feasibility are unverified.

See WORLD_MODEL.md, BATCH4.md and TARGET_LEDGER.md. Next decisive action: verify fabric-side strong ACK producer and compare mapped timing/area under equal-width shared, batched and dedicated links. No RTX 5090-class equivalence or novelty claim.
