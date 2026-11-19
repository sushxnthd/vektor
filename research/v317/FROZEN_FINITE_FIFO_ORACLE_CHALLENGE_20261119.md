# Frozen finite-FIFO bank-service challenge — 2026-11-19

**Status:** prospective protocol. Commit this file before creating the evaluator or inspecting confirmatory output.

## Question
Does the four-slot zero-cost bank oracle's instantaneous headroom transfer to a bounded-queue, bounded-arrival, bounded-output system? This is an *upper-bound falsifier*, not an implementable architecture or a rehabilitation of V317's physically falsified tile claim.

## Predeclared model
16-entry FIFO; four-entry scheduling window; four requests maximum output/cycle; two read ports per bank; each request needs two read operands and consumes both port reservations in the same cycle. Compare strict-order greedy (scan first four requests in order, accept if bank ports available) to a maximum-cardinality subset of the same four requests (lexicographic tie break). Both remove selected requests and preserve relative order of unselected requests. They see the identical pre-generated arrival sequence, so output cannot alter traffic generation. Both admit new requests only up to capacity and count dropped arrivals. No starvation/fairness guarantee for the oracle. Initial FIFO empty; warmup 2,000 cycles; measurement 20,000 cycles; arrival rate 3 requests/cycle. The frozen seeds are 11, 29, 47. Frozen regimes: uniform-16-bank (no-win prediction: <2% oracle advantage); 4-bank uniform and 65%-hot among four banks (conditional potential-win, not a guaranteed win); a 2-output/cycle cap as a no-win control; 1-request/cycle as a nonsaturated control. For hot-bank, bank zero has probability 0.65 and the other three each 0.35/3. Operand draws independent within request.

## Metrics and decision
Record admitted/dropped arrivals, grants, final occupancy, average occupancy, oracle/greedy throughput, and maximum waiting age. Predeclared relevance threshold >=1.02 on average per-cycle service, **with no increase in drop fraction**; reject positive transfer if service gain <1.02, output cap erases gain, or drops increase. Treat oracle as a generous impossible upper bound; a positive oracle result is NOT evidence of implementable GPU IPC. If fairness or bank-service assumptions break, report failure, do not tune thresholds or seeds. Preserve raw results and independently test grant feasibility, FIFO invariants and equal arrival streams.

## Physical gate
Prior compact greedy 21,314.6 um2 versus pairwise 21,324.7 um2 and electrical violations remain binding. No physical win without matched electrically legal routes, equal resources, and >=2% whole-proxy improvement. Do not merge the draft PR or claim RTX-5090 equivalence.
