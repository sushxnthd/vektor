# Vektor-059 preregistration

2026-10-09. Base Vektor-058 commit 4575cf311b7fe8373c091cfc2a8d178ee4a6db45. The 058 RTL was not previously simulated.

H59-A [DISCRIMINATION]: Python RTL nonblocking-semantic translation and independently structured UID transaction oracle agree on 10,080 original and 288×750 new cycles, varying N=1,2,3,4,5,8, age widths 2,3,4, stalls, duplicate tags, saturation and full simultaneous push/pop. Prediction: zero differences. This is NOT Verilog simulation.

H59-B [CAPABILITY-BUILDING]: C++ independent transaction-list implementation agrees on 43,200 frozen expected vectors. Prediction: zero differences.

H59-C [DISCRIMINATION]: instruction-only return tags are insufficient for concurrently outstanding out-of-order operands of one instruction. Predict a two-world indistinguishability counterexample. Construct 32×8×3 full-occupancy response identities and count collisions under 8-bit instruction-only tags versus composite 10-bit IDs.

H59-D [SURPRISE]: reserve 12.5% of 059 randomized probes for minimally guided non-power-of-two depths, duplicate tags, and saturation. Preserve negative results.

H59-E [CAPABILITY-BUILDING]: attempt free Icarus RTL simulation and Yosys generic synthesis; if unavailable mark inconclusive.

Adversarial roles: Explorer (operand-ID encoding), Skeptic (data conservation does not imply routing), Experimentalist (minimal collision), Analyst (software vs RTL separation), Anomaly Hunter (N and tag wrap), Prior-Art Auditor (no novelty claim), Replicator (C++), Theorist (pigeonhole ID lower bound).

Any mismatch falsifies H59-A/B. If explicit operand ID cannot distinguish the two worlds, H59-C fails. Equal cycle traces, reset, and queue capacity for paired controls. Single next decisive action: execute Verilog differential suite and synthesize, then implement operand-indexed scoreboard.
