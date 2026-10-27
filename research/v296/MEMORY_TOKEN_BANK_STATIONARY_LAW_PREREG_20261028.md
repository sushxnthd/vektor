# V296 finite-bandwidth bank-admission boundary: prospective test (2026-10-28)

## Scope and hard exclusion

This is a **synthetic mathematical prediction for the existing V296 bank-admission mechanism**, not a new architecture, an RTL timing claim, or a GPU speedup. V296 pairwise and strongest serial are functionally identical under the same issue/port resources, so this law must predict **exactly equal useful admissions per cycle**. Any positive relative performance claim additionally requires *both* contestants to pass the frozen D4/D8 extracted-RC physical gate, and measured tile clock, bandwidth, occupancy and traffic evidence. Preserve draft PR #13, branch `research/v296-pairwise-bank-conflict`, all prior failures, and sealed real-workload holdouts. V287 remains retired.

## Exact model, declared before evaluation

A saturated sequence of independent cycles offers S=4 priority-ordered slots to B=16 banks with P=2 physical read ports/bank. Each slot is independently valid with probability p (a **ready/occupancy proxy**, not measured GPU occupancy). First operand bank is uniform. Second operand copies the first with probability rho, otherwise draws an independent uniform bank. Two same-bank operands consume **two** read ports, never one. Every accepted wave costs one discrete shared bandwidth token. Before each cycle the bucket refills by integer r tokens, capped at K=4. Unused tokens carry to the next cycle. There are no FIFOs, burst correlations, operand coalescing, hidden ports, or per-warp latency in this law.

For available tokens t, derive exact finite-slot distribution Q_t(k) of k admitted waves by histogram dynamic programming, independently check small-B exhaustive enumeration, then derive the Markov transition for post-cycle tokens x: `P[x,y]=Q_min(K,x+r)(min(K,x+r)-y)`. Solve stationary `pi P=pi`; predict `q=sum_x pi_x sum_k k Q_min(K,x+r)(k)`. A strict upper bound is `q <= min(S*p,r)` in stationarity. At identical physical resources and clock `q_pairwise/q_serial = 1` exactly; if a measured candidate clock ratio g eventually exists, a *conditional fluid* upper envelope is `min(g*q,BW)/min(q,BW)`, with both q and BW expressed in compatible units. Do not label this envelope measured performance.

## Frozen prospective tests

Independent direct enumeration: B=2, S=2, P=2, p=0.7, rho in {0,0.3,1}, t in {0,1,2}; maximum probability error 1e-12. Stationary residual <=1e-10, probability mass conservation <=1e-10, and bounded `0 <= q <= min(S*p,r)`. Invalid probabilities, nonpositive resources, and invalid token budgets must fail closed.

Prospective synthetic Monte Carlo **unseen seeds** 812731 and 812737; 100,000 cycles/seed, discard first 10,000. Six fixed regimes: (p,rho,r) = (0.25,0,1), (0.75,0,1), (0.75,0.5,1), (0.95,0.8,1), (0.75,0,3), (0.95,0.8,3); K=4, B=16, S=4, P=2. The absolute prediction error per cell must be <=0.035 accepted waves/cycle. No parameters are fitted to prospective seeds. Pilot seeds 1201 and 1202 may be used only for implementation debugging; no regime/tolerance revisions after results. A failed cell must remain published as a failure.

The most important anticipated *non-win* regime is r=1 shared-bandwidth saturation: increased compatibility alone cannot exceed one wave/cycle on average, and cannot differentiate identical arbitration. The high-bandwidth regime r=3 is a **conditional opportunity** for a clock improvement, not a predicted observed V296 win.

## Limitations and physical decision

The i.i.d. slot model omits finite warp populations, dependency/scoreboard latency, queues, bank skew and burstiness; prospective success does not validate those transfers. This experiment must not open the existing real-GPU holdouts. Original D4/D8 physical experiment #40557136436 remains the primary kill gate. If matched timing/area/electrical constraints erase the advantage, reject V296's performance claim regardless of this law.
