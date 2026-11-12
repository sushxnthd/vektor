# V317 prospective integrated-control resource and occupancy boundary (2026-11-02)

## Frozen question and evidence tier
Does the **routed integrated 32-wave issue-control** area advantage, rather than the earlier isolated arbiter area, admit any defensible *conditional* tile-level gain once strongest-source repair, occupancy loss and shared traffic are included? This is a falsification of architecture extrapolation, not GPU performance measurement.

Use five already measured paired routed implementations: three placement seeds 7, 19, 37 (one independent seed set), and two density settings 0.05 and 0.35 (both reused seed 7). These are Nangate45 typical-corner 10-fF experiments with 356 FFs and **no RF SRAM or GPU datapath**. They are not five independent process samples. Area values (um2) source/pairwise: seed7 7426.72/6595.20; seed19 7539.50/6577.12; seed37 7367.67/6586.69; density0.05 7539.24/6609.04; density0.35 7407.83/6577.91. Freeze the five rows and do not select a favorable pair post hoc.

## Frozen model, strongest challenger and predictions
For each physical row j and variant x, let A_tile,x=A_other+A_issue,x, N_x=floor(B/A_tile,x), T_x=max(T_other,T_issue,x), and Q_x=min(L,C,N_x*u_x*r/T_x). u_x is an **explicit hypothetical effective active/accepted work fraction** (0..1), r=1 work/tile/cycle, L offered and C shared bandwidth in work/ns. Do not equate u with measured GPU occupancy or claim independence of bank conflict. At equal grants, ports and clock, there is no intrinsic per-tile throughput gain. Compare against a **hypothetically zero-area-cost timing-repaired original** at the same 2.20-ns other-tile period, which is deliberately stronger than the currently illegal 2-ns source. No claim that this repair exists physically.

Set A_other=40,000 um2 and B=1,175,000 um2 for W1/N1/N2. Freeze W1: u_s=u_p=0.75, L=C=100, T_other=2.20 ns, predicted 24 source vs 25 pairwise tiles for all five physical rows and G=25/24. Freeze N1: same but C=8 work/ns, predicted G=1 despite extra pairwise tile. Freeze N2: same as W1 but u_p=0.70 (u_s=0.75), predicted G<1 despite extra tile. Freeze N3: B=1,150,000, u_s=u_p=0.75, predicted 24/24 and G=1. Freeze transfer H1: B=1,175,000, u_s=0.80 and u_p=0.77, predicted G>1 only if 25*0.77>24*0.80. These are *synthetic* regimes, not tuned benchmark traces.

## Prospective adversarial tests
1. Compute the **robust budget interval** on which all five pairwise rows fit 25 tiles while every source row fits only 24, using max pairwise area and min source area, not the favorable paired row. Test both endpoints and one outside point by independent integer enumeration.
2. Derive occupancy break-even u_p/u_s > N_s*T_p/(N_p*T_s) when no demand/bandwidth saturation. Verify against deterministic independently generated finite-horizon activity streams (fixed seeds not used for law construction), including a negative occupancy-control and a bandwidth kill. Report tolerances and deviations, not only pass flags.
3. Verify the strong-source clock repair control: if T_other=2.20 ns, repairing the source from slightly over 2.0 ns to 2.0 ns has **zero modeled throughput effect**; no source legality or new timing closure is implied.
4. Preserve counterexamples and reject any unconditional GPU speedup claim. Do not relabel this conditional resource model as a new hardware mechanism.

## Decision
A model that fails any frozen prediction is falsified or revised with a new prospective protocol. Even a complete pass only validates arithmetic and a synthetic activity executor; the next physical gate remains legal source timing repair and SRAM/datapath-integrated placement with realistic port traffic, switching activity and multi-corner timing. Keep existing V317 branch/draft PR #34, and do not modify Kernellum PR #119.
