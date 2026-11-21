# Frozen periodic bank-conflict transfer gate (2026-11-02)

## Status and selection bias
This protocol is committed **before** running the independent held-out perturbation experiment. The positive candidate below was **discovered by an exploratory search over 1,600 synthetic periodic traces** with short 350-cycle evaluations. It is NOT a prospective discovery; only the subsequent seed/perturbation tests are prospective. Preserve this selection bias in every report.

## Fixed hardware/service abstraction
Four candidate requests from the head of an eight-entry FIFO; each request needs two bank reads; five banks with two reads/bank/cycle; maximum four completed requests/cycle. Every nonempty cycle MUST serve the oldest resident request. External offered requests queue in an unbounded source backlog, not counted as on-chip storage. Admit to FIFO before scheduling; no dropping. Four offers per cycle. The study is synthetic, not RTL, GPU IPC, SRAM, or an RTX 5090 model.

## Fixed policies
- `greedy`: oldest-to-newest feasible grant.
- `reverse`: grant oldest, then greedily newest-to-oldest.
- `least_overlap`: grant oldest, then pick feasible request minimizing count of shared occupied banks; ties oldest-first.
- `bestfit`: grant oldest, then choose feasible request minimizing squared bank-load imbalance; ties oldest-first.
- `exact_head`: enumerate every feasible subset containing oldest, maximize cardinality, break ties lexicographically oldest-first.
The **strongest equal-service-resource comparator** is the best sustained throughput of all four simple policies, selected per regime. These are not matched physical area/cell-cost implementations.

## Frozen candidate
Two-phase repeated stream, four offers per phase:
```
phase 0: (3,4), (1,4), (2,4), (0,0)
phase 1: (3,1), (1,1), (3,3), (4,0)
```
The exploratory 350-cycle result was exact_head 1120 completions versus 933 for each of four simple controls (1.20043x). This is discovery/training evidence only, not a holdout.

## Frozen holdouts and predictions
Three previously unused seeds: 4919, 7351, 10657. Each: 1,000 warmup + 5,000 measured cycles. No selection/replacement of seeds or workloads after evaluation. Four offered requests per cycle, preserving request order.
1. `periodic_clean`: exact repeating two-phase sequence, phase offset = seed % 2. **Predicted win** exact_head / strongest simple >=1.10.
2. `periodic_noise1`: each operand independently replaced with a uniform 0..4 bank with probability 0.01. **Predicted win** >=1.02.
3. `periodic_noise5`: same with probability 0.05. **Exploratory transfer**: no numerical success claim frozen.
4. `periodic_cap2`: clean stream but output cap two. **Predicted no-win** ratio <=1.01.
5. `uniform16`: independent uniform 16-bank requests, two operands/request, four offers/cycle. **Predicted no-win** ratio <1.02. Bank count changes to 16 only for this negative control.

Report every regime even on failure. No post-hoc change to thresholds. For any sustained stream, use the necessary demand ceiling `T <= min(lambda,K,min_b P_b/d_b)`, but do not treat it as sufficient or a novel positive law. The positive mechanism is not promoted without workload-derived occurrence, equal-resource RTL, legal electrical timing, and a compact prospective predictor that survives unseen workloads.

## Required checks
Independent implementation without importing evaluator; request conservation (offered = completed + FIFO + upstream); finite FIFO occupancy; oldest grant each nonempty cycle; matching deterministic holdout outputs; per-bank ports; compare strongest control, not only serial greedy. Keep PR #34 draft, one existing research branch; never erase negative V317 evidence.
