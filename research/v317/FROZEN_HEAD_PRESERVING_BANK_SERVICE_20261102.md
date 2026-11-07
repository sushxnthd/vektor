# Frozen head-preserving bank-service oracle falsification (2026-11-02)

## Scope and non-promotion
V317's integrated-area claim is killed by the compact-greedy control and illegal electrical routes. This experiment is **not** a new architecture mechanism; it tests whether the previously reported unconstrained bank-service oracle relies on bypassing the oldest valid request. The single active draft PR remains #34; no second mechanism, branch, or PR. Results are synthetic combinational upper bounds, not GPU IPC or physical signoff.

## Exact semantics
Four requests, two independently consumed operand reads per request, two read ports per bank, no merging for equal-bank operands. Compact greedy processes valid slots 0..3 in age order, admitting each request if bank ports allow. Unrestricted oracle enumerates all 16 masks and maximizes admitted count. Head-preserving oracle also enumerates all 16 masks but **must admit the oldest valid request** (always individually feasible); among masks meeting that condition it maximizes admitted count. For cap K=2,4, compare min(K, admitted count), with the cap applied after bank admission as an optimistic service bound. A head-preserving grant is only a necessary, not sufficient, condition for starvation freedom. No queue evolution or latency claim.

## Predictions frozen before implementation and evaluation
- Constructed head blocker: [(0,1),(0,0),(1,1),(2,2)], K=4. Greedy=2, unrestricted=3, head-preserving=2; **predicted no win under head preservation**.
- Disjoint control: [(0,0),(1,1),(2,2),(3,3)], K=4: all grant 4.
- Uniform 16-bank random operands: **predicted no material head-preserving gain** (ratio <1.02).
- Hot bank with P(bank0)=0.65, remaining banks uniform among 1..15, K=4: **candidate predicted-win regime** (head-preserving ratio >=1.02). If false, reject; do not retune.
- Same hot mixture, K=2: predicted no-win (<1.02) due to output cap. If false, preserve the falsification.

## Prospective test
Three independent seeds 4127, 6151, 8111; 10,000 independent four-request batches/seed for each of five scenarios: uniform16/K4, uniform4/K4, hot65_16/K4, hot65_16/K2, samebank70_16/K4 (source1=source0 with 70% probability, otherwise independent uniform banks). All four valid. For each report raw total greedy, head-preserving and unrestricted grants, mean ratios, frequency of improvement and of unrestricted improvements requiring head bypass, and the exact accounting identity H/G = 1 + sum(H-G)/sum(G). Never silently discard a case where head-preserving exceeds unrestricted or falls below greedy.

## Independent checker
Implement a separately coded recursive subset search, exhaustive B=2 and B=4 over all 2^8 and 4^8 four-request tuples, plus separately seeded random holdouts. Test constructed controls and count invariants. A discrepancy falsifies the evaluator. Enumerations and sampling are workload models, not measured silicon behavior.

## Decision
No positive mechanism is promoted on a head-preserving oracle win alone. If uniform16 head-preserving <1.02 and/or hot65 fails >=1.02, preserve the negative evidence. If hot65 survives, the next gate is a finite-buffer, age-aware, same-port scheduler with strict latency-tail controls, and a competent matched RTL physical baseline. The original V317 area and electrical failures remain binding.