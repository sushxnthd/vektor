# V145 ARCHITECTURE ledger — 2026-10-13
Candidate block: fixed parity dual response, 2 x Wave32 physical return vectors; port 0 even banks, port 1 odd banks; bank(reg)=reg_id%16. 3 destination slots, duplicate-tag multicast.
Comparison: V144 fully flexible dual return, same bus count and word width. Fixed wiring may simplify input network, but V144's RTL does not include upstream bank-to-bus fabric; generic cell counts alone cannot compare whole return-network cost.
Cycle model: 214 synthetic FP32 program configurations, 1 representative lane/wave, identical RF reads and final state; fixed parity is substantially slower, especially parity-hot traces. Not physical throughput.
**Decision:** Do not adopt fixed parity as V-Tile default without a decisive synthesis+equal-area result. Preserve flexible dual return as provisional candidate.
**Build:** synthesizable fixed-parity router, full-Wave32 differential bench against V144 on legal ordered responses, parity-negative tests, CI Yosys/Icarus workflow.
**Gates:** RTL pending CI; generic synthesis pending CI; FP32 arithmetic integrated tile INCONCLUSIVE; graphics/tensor/memory/software/PPA INCONCLUSIVE; RTX 5090-class INCONCLUSIVE.
**Single next decisive action:** run CI and inspect mapped logic; if fixed router's savings are insufficient to offset >26% mean modeled cycle loss, close this kernel and integrate flexible dual response into actual FP32 collector/scoreboard.
