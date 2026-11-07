# V317: request-order identifiability falsification (2026-11-03 UTC)

Evidence tier: exhaustive synthetic four-slot/two-read-ports-per-bank combinatorial model; **not** GPU trace, RTL timing, routed electrical legality, or GPU IPC.

## Question
Does recording the complete histogram of unordered operand bank pairs (rather than only marginal bank counts) suffice to predict the greedy scheduler's four-slot completion?

## Exact counterexample
For two banks, four requests consisting of two (0,0) and two (0,1) requests have exactly the same joint pair histogram under both orders:
- [(0,0),(0,0),(0,1),(0,1)]: greedy completes 1.
- [(0,1),(0,1),(0,0),(0,0)]: greedy completes 2.
The maximum-cardinality oracle completes 2 in either order. Thus the oracle/greedy ratio changes from 2.0 to 1.0 despite identical joint pair demand.

## Exhaustive audit
Enumerate all size-four multisets of unordered bank pairs, and all distinct permutations of each multiset. With two read ports per bank and four candidate slots, count multisets with more than one greedy completion outcome. Counts: B=2: 6; B=3: 48; B=4: 238. The oracle optimum is invariant under every permutation, verified independently by exhaustive subset search in the checker. Reproduction: `python3 research/v317/request_order_identifiability.py`.

## Implications and limits
The previous marginal-histogram identifiability failure cannot be repaired merely by collecting pair co-occurrence frequencies. A prospective predictor for this specific greedy arbiter must preserve request order, or explicitly model the ordering process. This does not show that an implementable maximum-cardinality scheduler has net throughput advantage; the previously established compact-baseline area and electrical failures remain binding. Do not promote V317 or claim tile-level gains. Next decisive gate: provenance-pinned real workload request sequences plus legal matched-resource RTL and timing.
