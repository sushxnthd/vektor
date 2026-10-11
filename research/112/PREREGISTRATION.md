# Vektor-112 preregistration (2026-10-11)
Classification: DISCRIMINATION and CAPABILITY-BUILDING.
Predictions fixed before the local run:
P1: V111's documented globally unique tid cannot be replaced by raw Vortex lane-local tid. Composite logical thread (core,CTA,warp,lane) admits independent private-memory reversals that naive numeric-tid ingestion rejects.
P2: Same-thread, overlapping CTA-shared and global hazards remain ordered; event duplication/loss and mixed-CTA cohorts remain rejected.
P3: Issue-stage virtual addresses do not establish physical aliasing, DRAM traffic, cache misses or retirement order.
P4: Source-pinned patch fails closed if its expected anchors change.
Seeds: discovery 112000..112191 (192), holdout 912000..912095 (96), surprise 712000..712035 (36; 11.11% of 324); six schedule variants per seed plus seven directed controls. Exact reversal counts not preregistered. No GPU performance improvement predicted.
