# V276: warp-static selectable RF bank hash

Evidence E0; sole active kernel. No tile change.

1. Law: for two simultaneous operands and four single-read banks, T=2-c, where c is bank-collision probability. Gain G=r*min(m,2-c_adapt)/min(m,2-c_bestfixed).
2. Mechanism: choose one fixed bank hash per warp at allocation; direct bank=reg[1:0], or XOR bank=reg[1:0]^reg[3:2]. Apply the same mode to every read and write; never live-remap.
3. Controls: best fixed direct and fixed XOR hashes, same banks, ports, queue, buffers, and arbitration; include area-matched fixed-hash scheduling.
4. Boundary: for fraction p of pairs (16k,16k+4) and 1-p of (16k,16k+5), adaptive ideal T=2 and best fixed T=1+max(p,1-p). Gain=2/(1+max(p,1-p)); maximum 4/3 at p=.5; no win at p=0 or 1.
5. RTL: two-request bank decoder/arbiter, no extra RF port; full storage decoder and warp-mode lifetime check still required.
6. PPA: mapped Nangate45, clean STA cap/slew, wire/load sensitivity, switched-capacitance and mode-distribution overhead.
7. Workloads: compute/memory/divergent traces, RF operands/cycle, stalls, utilization, energy and timing.
8. Falsify on mapping mismatch, illegal double-read, resource increase, no area-matched benefit, failed STA or holdout disagreement.
9. Frozen unseen: p=.6 predicts 1.25x ideal, p=1 predicts 1.0x; not opened before physical gates.
10. Consequence: only integrate a warp-static mode bit after complete physical validation.

Prior art: XOR banking and programmable bank mapping are established; no novelty claim. Synthetic throughput is not measured GPU performance.
