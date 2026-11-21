# Frozen V317 two-cycle clairvoyant head-preserving ceiling (2026-11-03)

## Scope and evidence tier
A *negative-control / opportunity-bound* experiment for the existing bank-port scheduling workstream, not a new architecture mechanism. Four initially valid, ordered requests; each requires two bank reads; each bank has two read ports; at most two requests issue per cycle; no new arrivals; both cycles require oldest-pending service and legal bank capacities. No GPU traces, RTL PPA, sustained IPC, SRAM signoff, or RTX-class claims.

## Policies and independent tests
Compare compact oldest-first greedy, existing conflict-degree head-first heuristic, and an exact two-cycle upper bound that enumerates first-cycle feasible head-preserving choices and second-cycle feasible head-preserving choices. A compact *tail-compatibility* policy must equal the exact oracle for four requests if it chooses a head-compatible second request leaving the remaining two mutually compatible when possible; otherwise it falls back to compact greedy. Verify the exact identity on exhaustive three- and four-bank spaces, then evaluate unseen five-bank exhaustive vectors and independently seeded 16-bank random holdouts. Independent checker must not import evaluator.

## Frozen hypotheses (before results)
1. Exact opportunity identity: oracle minus greedy equals one **iff** greedy issues two in cycle one, leaves an incompatible residual pair, and some legal head-plus-partner choice leaves a compatible residual pair; otherwise zero.
2. Tail-compatibility must match exact two-cycle oracle for every enumerated vector.
3. On unseen uniform 16-bank random vectors, oracle/greedy <= 1.01; on exhaustive five-bank vectors oracle/greedy >= 1.001. Failures are retained.
4. Compare with degree-head as a strong adversarial control. Do not claim an implementable gain from a clairvoyant batch oracle. Hardware, finite FIFO, arrivals, latency, and physical wiring are missing and remain kill gates.

## Fixed protocol
Exhaustive B=3,4,5: all B^8 ordered four-request vectors. Prospective B=5 is evaluated only after this file is committed. Uniform B=16: seeds 1603, 2603, 3603; 12,000 vectors per seed. Ports=2, issue cap=2, cycles=2. Record counts, ratios, opportunity frequencies, and exact prediction checks. Preserve failed hypotheses and raw reproducible JSON.
