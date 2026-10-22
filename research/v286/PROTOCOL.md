# V286: Warp-index-conditioned register-bank permutation

Status: sole ACTIVE research kernel after V285's mapped-area retirement. E0 only.

1. Bottleneck: with two RF read slots/bank, any issue group needs at least max_b ceil(n_b/2) bank-service cycles. Cross-warp correlated logical bank indices can dominate this bound.
2. Mechanism: physical_bank = (logical_bank + wave_id[3:0]) mod 16. Apply identically on RF write allocation, RF reads, and bypass bookkeeping. For each warp this is a bijection, so the same RF storage capacity and ports are preserved.
3. Strong controls: unsalted bank index, warp-XOR bank salt, alternative invertible affine/GF(16) warp hashes, and bank-aware compiler mapping. Do not claim novelty if a cheaper hash matches the result.
4. Predicted win: W<=4 distinct wave IDs, same two logical operand banks, can spread demand from one or two hot banks across four banks. Gain only if RF-bank service is the critical resource.
5. Smallest RTL: 4-bit adder per bank address; no new ports, buffers, banks, or register storage.
6. Physical proxy: matched Nangate45 synthesis, mapped area, combinational path, max-cap/slew and load/wire sensitivity if STA becomes available.
7. Workload: independent grant counts and multi-cycle replay cycles; then integrate real compute/memory/divergent traces.
8. Falsification: if a simpler XOR/GF(16) permutation with <= area and delay matches all wins, or if storage/row addressing cannot preserve read/write coherence, retire.
9. Frozen unseen prediction: additive beats XOR on wave-ID-correlated operand indices, ties on identical hot-bank indices, near-ties on independent indices. Freeze before opening holdouts.
10. Consequence: V-Tile needs explicit physical RF bank/row address mapping before this can be integrated; modifying only the arbiter would be incorrect.

Prior art: warp-index-aware RF layout and bank swizzling are established ideas. See https://patents.google.com/patent/EP3915009B1/en and https://arxiv.org/abs/2010.09330. This is a targeted engineering search, NOT a field-level novelty claim.

No RTX 5090-class performance or energy claim. V153/V156 FP32 cutset electrically disqualified. Hourly automation unchanged.
