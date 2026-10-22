# V291: same-cycle RF read multicast

Evidence E0. Sole active hypothesis. V287, V289, V290 retired.

Bottleneck: duplicate physical register reads compete for limited bank ports. Exact mechanism: one read can feed multiple waiting collectors only if physical address, warp/lane identity and register version match.

Law: if bank b has n_b pending operands but u_b distinct full physical addresses, ideal read service cycles fall from max_b ceil(n_b/P_b) to max_b ceil(u_b/P_b), conditional on fanout F, timing and output bandwidth. This is an upper bound, not measured throughput.

Strongest controls: conventional collector; equal-area operand cache with matching tag comparison and broadcast; any existing multicast.

Frozen positive: four simultaneous identical-address reads, one bank port, four collector destinations, predict one RF read rather than four, subject to feasible fanout.
Frozen no-win: four distinct-address reads on one bank, predict four RF reads for both and no throughput win.
Frozen adverse: same logical register number from different warp IDs must not coalesce.

Smallest RTL: four request inputs, one bank port, full-address/version equality, one read value distributed to existing collectors. Verify RTL, synthesize and characterize area, STA, max-cap/slew, switching energy and wire/load sensitivity. Then test compute, memory and divergent workloads and unseen holdouts.

Kill if physical duplicates are rare, strongest equal-budget control matches, or fanout/timing/area eliminates gain. Prior art: BOW (MICRO 2020), Memento (ISCA 2024), CORF (2019), Warped-Compaction (HPCA 2025). No novelty or RTX 5090 claim.
