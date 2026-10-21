# V262 E0 frozen protocol (original in reproducibility ZIP)

Sole mechanism: 4x16-bit warp request addresses encoded as base16+three signed 5-bit deltas in 1x32-bit beat if all deltas in [-16,+15]; else 2 raw beats. All controls use identical 32+1 wires, same mode bit, ports and buffering. Ideal link-only gain G=2/(2-p); after clock retention r, G<=2r/(2-p). Strong controls: coalesced raw link, optimized base+delta packetizer with identical resources, fully pooled scheduler. For r=.95, >10% link-bound gain vs raw requires p>.2727.

Physicality: functional -> RTL simulation -> synthesis -> max-cap/slew -> matched STA/area -> workload traffic/throughput -> 0.5/1/2x wire/load sensitivity. Kill on decode failure, matched control equivalence, or physical energy/timing loss. Freeze seeds positive 262101 (4096 groups, ~85% compressible, link-bound), negative 262102 (~4%, compute-bound), divergent 262103 (~8%, memory-bound). Target >40% beat reduction and >10% modeled positive gain vs raw; <=1% gain on negative and divergent. Evaluate matched packetizer. No tile change without physical PPA and novelty.

See full frozen protocol in V262 retirement ZIP. V153/V156 remain electrically disqualified.
