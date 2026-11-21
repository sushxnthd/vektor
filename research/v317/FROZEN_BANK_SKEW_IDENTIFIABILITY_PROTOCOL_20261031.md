# V317 bank-skew identifiability falsification: frozen protocol (2026-10-31)

## Research question

Does a no-win certificate based only on **aggregate** physical register-file (RF) demand and total RF ports remain valid when read demand is nonuniform across banks? This is a *falsification of an assumption in V317's earlier aggregate envelope*, not a new GPU mechanism. No hardware claim or NVIDIA bank mapping is implied.

## Frozen synthetic counterfactuals (specified before the new implementation and independent test)

Two identical bank capacities: P=(2,2) read units per cycle. Issue and ALU ceilings: W=A=5/4 instructions per cycle. Physical reads per instruction: D=3 in both worlds. Candidate can remove exactly K=1/2 read per instruction **from bank 0 only**, with zero assumed clock/control overhead. The same fixed two banks, capacities, and savings budget are used for both baseline and candidate.

- **Predicted no-win:** balanced reads d=(3/2,3/2), d'=(1,3/2). Exact per-bank gain should be **1**.
- **Predicted win:** skewed reads d=(5/2,1/2), d'=(2,1/2). Exact per-bank gain should be **5/4**.
- **Aggregate-only model:** D=3, D'=5/2, P_total=4, W=A=5/4. Predicts **1** for *both* worlds. Thus aggregate no-win inference must be rejected as nonidentifiable, despite identical aggregate observables.

## Frozen unseen-distribution sensitivity

Enumerate every feasible nonnegative bank-demand allocation with total D=3 in steps of 1/2, subject to bank-0 savings K=1/2. Compute the exact min/max gain and compare with a separate independent oracle. No cherry-picking allocations after seeing results. Predicted interval **[1,5/4]** (can be verified algebraically from the listed capacities). This is an exhaustive *six-point synthetic domain*, not real unseen GPU traces.

## Law and gates

Under an optimistic steady-state independent-bank capacity envelope,
lambda0 = min(W,A,min_b P_b/d_b), lambda1 = min(W,A,min_b P_b/(d_b-k_b)).
A safe sufficient no-win criterion for **nonnegative overhead and read-elimination-only candidates** is that *every* bank satisfies P_b/d_b >= min(W,A), not merely that sum(P_b)/sum(d_b) >= min(W,A).

Independent test must verify exact rational arithmetic, shared capacity/savings, aggregate-observable equivalence, six-point enumeration, and the no-win/win counterexample. Treat ideal steady-state rates as resource ceilings, not measured IPC; no dynamic bank mapping, cache hit, instruction readiness, compiler, routing, or PPA evidence is available.

## Kill/revise

If the counterexample fails, retract the claim. If it passes, retract **aggregate no-win as a general banked-RF certificate** and restrict the earlier V317 no-go to explicitly pooled RF or independently verified balanced per-bank demand. Do not promote any architecture or make RTX 5090 equivalence claims.
