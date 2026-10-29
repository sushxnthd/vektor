# V307 exact bank compatibility diagnostic (pilot only)

For k independently sampled 2-bank operand masks from B banks, the probability that all k requests are mutually bank-disjoint is

P_k(B) = product_{i=0}^{k-1} [ C(B-2i,2) / C(B,2) ],

with P_k=0 when B<2k. This is a classical occupancy/combinatorial identity, not V307 novelty. At B=8, P_2=15/28=53.5714%, P_3=90/784=11.4796%.

The frozen **opened pilot** traces were audited without retuning policy parameters. For each of four seeds, 48 instruction positions and all C(5,k) warp subsets, count exact disjoint masks:

| Regime | Compatible pairs / 1920 | Compatible triples / 1920 |
|---|---:|---:|
| W1 iid random bank pairs | 998 (51.9792%) | 219 (11.4063%) |
| N1 rotating pairs, 5% random | 1660 (86.4583%) | 1202 (62.6042%) |
| N2 fixed warp pair | 1728 (90.0000%) | 1344 (70.0000%) |

The W1 pair/triple rates are consistent with the exact iid law. The structured regimes are deliberately outside its independence assumption. This diagnostic predicts *compatibility*, not the advantage of PRESSURE over FUTURE-TIE, nor end-to-end GPU throughput. It does not rescue the pressure sufficiency counterexample. Any future throughput law must additionally account for arbitration policy, occupancy, collector buffering, per-bank ports, dependencies, wire delay and control overhead.

Reproduce: `cd research/v307 && python3 boundary_audit.py`. Holdout seeds 2001–2020 remain unopened.
