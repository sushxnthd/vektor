# Vektor run30 — V281 retired; V282 active (2026-10-22)

## V281 decisive falsification

The projected max-clearance selector agrees with its max-plus algebra on 1,048,576/1,048,576 input states, but the experiment's objective is SUM of normalized queue backlogs, not MAX. A same-input metric-consistent one-step greedy control differs on 101,232 of 1,048,576 states. Against stronger controls V281 wins 0/36 training cases by >1% and loses 16/36. Its previously frozen positive holdout failed: gain 0.95381793993 (<1.01 required). Negative holdout passed: gain 1.0. Retire V281. This is model-level falsification, not an electrical PPA result.

Icarus/Yosys/OpenROAD were unavailable in the run environment; public package-manager installation timed out. No fresh characterized STA, clean cap/slew, or RTL simulation. FP32 V153/V156 remain electrically disqualified. Integrated tile unchanged.

## V282 — sole active kernel: bank-local 2x2 response queues

1. **Law:** strict-FIFO recoverable service is bounded by P(head blocked AND later request ready). This is a bound, not measured GPU throughput.
2. **Mechanism:** four slots split into two bank-local 2-deep FIFOs, one input, one output, bank-ready mask and RR bank selection; per-bank FIFO ordering.
3. **Strongest equal-budget control:** global four-slot fullscan4 oldest-ready selection, same storage and ports. Additional strict FIFO and two-head lookahead controls.
4. **Boundary:** medium bank-blocking with mixed bank arrivals can beat two-head lookahead; skewed arrivals overflow partition and lose to fullscan4; compute-bound light arrival no win.
5. **RTL:** two 4-slot-equivalent modules (banked and fullscan), with directed smoke TB prepared but not yet executed.
6. **PPA:** characterize mapped area, timing, max-cap/slew and energy proxy at matched loads; 0.5x–2x output load sensitivity. None yet measured.
7. **Metric:** modeled completed requests/cycle, source backpressure and total pending requests; not IPC.
8. **Falsification:** if fullscan4 has <= area/delay/energy and >= throughput, retire; if frozen positive/no-win/loss predictions fail, retire.
9. **Unseen:** frozen positive, no-win and loss cases; unopened.
10. **Tile consequence:** only integrate if physical Pareto improvement is validated; otherwise unchanged.

E0 training: 36 configurations; banked beats two-head by >1% in 10, beats fullscan4 in 0, loses to fullscan4 by >1% in 14. Max banked/two-head gain 1.183x but banked/fullscan4=0.847x in that case. No breakthrough established.

**Prior art:** banked FIFO scheduling already described in *Complexity Effective Memory Access Scheduling for Many-Core Accelerator Architectures* (2009); GPU memory request reordering in MRPB (HPCA 2014, DOI 10.1109/HPCA.2014.6835938); bank-partitioned queues in US8854387B2. No novelty claim.

**Acceleration rule:** next substantive V282 run must execute matched RTL/physical discriminator or retire. RTX 5090 remains reference only.
