# V271 priority collision and physical gate (2026-10-22)

**Closest primary source:** Yongbin Gu and Lizhong Chen, "Dynamically Linked MSHRs for Adaptive Miss Handling in GPUs," ICS 2019, DOI 10.1145/3330345.3330390, author manuscript: https://web.engr.oregonstate.edu/~chenliz/publications/2019_ICS_Dynamcially%20Linked%20MSHRs.pdf

The published DL-MSHR dynamically allocates MSHR resources from a shared pool to adapt to different primary/secondary miss patterns, explicitly addressing fixed-capacity underutilization. It reports IPC, area, power and energy comparisons. The V271 3+3+2 fixed-reservation/shared-spill policy is **not novel at the level of dynamic credit pooling**. Its potential distinctness is only a constrained local allocator that could preserve near-global admission throughput with lower physical control/wiring cost; that claim is untested.

The paper reports a 2-cycle DL-MSHR access delay vs a 1-cycle assumed conventional MSHR in a sensitivity study. This emphasizes the need to account for allocator latency, not just successful admissions.

Training E1 model at service latency 30: alternating-skew mean completion latency hybrid 32.1198 cycles vs best fixed 46.2662, but global 31.6772. Balanced hybrid 31.9775 vs fixed44 31.8764; single-skew hybrid 343.8003 vs fixed62 43.0086. Frozen seeds are unopened.

**Decisive next gate:** Run actual V271 RTL scoreboard and Nangate45 mapped synthesis of all seven configurations; then one characterized matched electrical comparison of hybrid vs global with clean max-cap/slew and realistic wire/load. Include an extra-cycle hybrid admission penalty and a DL-MSHR-inspired dynamic-pool control before considering novelty. If physical PPA cannot beat the stronger fully shared control, retire without further wrappers. No integrated-tile changes.

Existing generic repository CI passing does not imply V271 RTL was simulated. An attempt to extend the GitHub workflow was blocked; do not mislabel that as physical failure.