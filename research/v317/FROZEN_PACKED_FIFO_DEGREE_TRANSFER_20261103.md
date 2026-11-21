# Frozen V317 packed-FIFO eligibility and output-cap transfer (2026-11-03)

## Motivation and prior knowledge
V317 degree-head RTL passed 4,096-case B=2 simulation and synthesized to 734 generic cells versus 260 for compact greedy (hosted run 41509686509). The earlier exhaustive B=3 study reported 158,529 versus 158,409 aggregate grants across **all 16 valid masks**, including head-invalid and holey masks. Those masks are not representative of a packed, oldest-first four-entry FIFO. This protocol tests whether the claimed tiny service benefit survives a realistic eligibility restriction. It does NOT revive V317's failed physical-area claim.

## Model and strongest control
Four request slots; two charged operand reads per request, two ports per bank, oldest valid request mandatory; output cap K in {2,3,4}. Greedy scans slots 0,1,2,3. Degree-head scans slot 0 then other slots in ascending number of valid, bank-overlapping neighbors, breaking ties by slot index. Exact head-preserving cardinality oracle is a **nonphysical upper bound**. Each policy has identical bank ports and output cap. Grant count is instantaneous, not sustained throughput.

## A priori structural predictions
1. For **head-valid** windows and K<=2, greedy, degree and exact-head have identical grant cardinality on every legal request vector. This follows because all three serve the head; if any other request can be added, the greedy scan finds one. Head-invalid masks are explicitly outside this theorem.
2. With B<=3, each request charging two reads and each bank having two ports, at most B requests can be admitted, so K=4 and K=3 grant counts coincide.
3. In a packed FIFO, valid masks must be a prefix of ones: 0001,0011,0111,1111 (or 0000 for an empty queue). Retrospective B=3 analysis of these masks will be reported separately from the prospective B=4 transfer.
4. Prospective **unseen B=4** transfer: on 40,000 independent uniform operand vectors for each seed 191,409,733, all four slots valid, degree/greedy aggregate grant ratio at K=3 and K=4 will be **<1.005**. At K=2, the ratio must be exactly 1.000000. This is a falsifiable small-headroom prediction; a ratio >=1.005 refutes it.
5. A positive degree result is not sufficient to promote hardware: it must beat compact greedy in finite FIFO throughput, legal matched routed timing/area and workload-derived bank traces. Previously failed RF-proxy physical gates remain failed.

## Evaluation and independence
The evaluator will report all 16-mask B=3 exhaustive totals and packed-prefix subtotals, and the frozen B=4 seeded holdout, including per-cap gains, losses, and head-valid/head-invalid contributions. An independent checker will separately verify the K<=2 head-valid theorem on exhaustive B=2/3, the B<=3 capacity ceiling, and reproducibility of the frozen B=4 random stream. The checker must not import the evaluator's policy implementation. No post-outcome seed, threshold, or model edits. If results contradict any prediction, preserve them.

## Research decision rule
If the head-valid packed-FIFO gain is below 0.5% even at the combinational grant tier and degree remains 2.82x generic cells, **reject degree-head as a cost-credible architecture candidate** absent workload evidence that independently predicts a larger gain. Do not conflate this with a new physical-route result, GPU IPC, or RTX-5090-equivalent performance.
