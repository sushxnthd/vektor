# V317 prospective finite-buffer bank-port falsification (2026-11-02)

## Status and immutable hypotheses

This protocol is frozen **before** implementation or results. Continue the single V317 pairwise bank-credit controller mechanism on `research/v317-sass-provenance-gate`, draft PR #34. Do not substitute the historical V287 mechanism. Existing routed controller areas at 2.050 ns (source 7244.78, pairwise 6576.58 um2) and 2.200 ns (7096.08, 6560.36 um2) support **only** a hypothetical 24-versus-25 tile budget under 40,000 um2 non-controller area/tile and a 1,170,000 um2 total budget. This is not a physically implemented tile.

The previous unbounded-queue workload transfer cannot establish finite-buffer performance. The decisive test here introduces 4-entry per-tile FIFO, 8-entry shared output FIFO with same-cycle bypass, one read/issue per bank per cycle, fixed shared output bandwidth, round-robin bank arbitration, backpressure and per-tile eligibility. Each tile produces one attempted operation per cycle until its FIFO fills; a bank ID is sampled uniformly when admitted. A blocked head retains its bank ID, creating real head-of-line correlation. Source has q=1. Pairwise has eligibility q in each cycle. This is a **synthetic structural traffic model** with no actual SRAM or RF port RTL.

## Predictions frozen before simulation

For N tiles, B uniformly selected single-port banks, per-tile independent issue eligibility q, and C shared operations/cycle, the **independent-head occupancy law** predicts E[min(K,C)], where P(K=k) is computed by exact dynamic programming over N independent tile opportunities. A new tile activates bank k with probability q/B; transition from k occupied banks to k+1 occurs with probability q(B-k)/B. This is a predictive *null*, not a guaranteed law once finite queues create correlated head-of-line blocking. Compare pairwise N=25 with source N=24.

| Regime | B | C | pairwise q | Frozen independent-head throughput ratio | Interpretation |
|---|---:|---:|---:|---:|---|
| W_ports | 32 | 32 | 1.00 | 1.02735253 | predicted win smaller than 25/24 |
| N_ports | 4 | 4 | 1.00 | 1.00025110 | predicted no-win from port saturation |
| R_eligibility | 32 | 32 | 0.85 | 0.91859780 | predicted loss |
| N_bandwidth | 32 | 12 | 1.00 | 1.00001452 | predicted shared bandwidth no-win |
| H_marginal | 32 | 32 | 0.95 | 0.99249186 | predicted sign reversal near boundary |

Frozen seeds: 17, 71, 173. Warmup: 2,048 cycles; measured: 30,000 cycles; tile FIFO depth 4; output FIFO depth 8; 24 source / 25 pairwise tiles. Use a deterministic random generator, separate independent simulations for each variant and seed. Report completed throughput, stalls, blocked admissions, maximum occupancies and all per-seed ratios. The independent-head law must be implemented separately from the event simulation. **Falsify** the null law for any regime whose three-seed mean differs by more than 0.015 absolute ratio. Do not fit parameters after outcomes. Also test equal-resource 24-versus-24 q=1 at B=32,C=32; expected exactly 1.000x in distribution, tolerance 0.015.

## Interpretation

Even a successful synthetic test is not SRAM macro timing, actual GPU IPC, measured activity power, or evidence of novel throughput. If HOL correlations break the independent-head law, preserve the falsification and derive a corrected bound before future unseen transfer. No unbounded queues; any blocked or dropped attempted work must be counted. No claim of RTX-5090 equivalence. The next hard gate remains actual RF SRAM and datapath RTL integrated in matched tile P&R with real traffic traces and multi-corner timing.
