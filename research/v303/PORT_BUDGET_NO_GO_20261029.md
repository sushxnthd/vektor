# V303 finite-port coherence: frozen no-go (2026-10-29)

## Decision
**Retire V303's opportunistic one-port update mechanism.** The precommitted survival criterion in [PORT_BUDGET_PROTOCOL.md](PORT_BUDGET_PROTOCOL.md) failed in H2. Do not reframe the H3 result as a prospective success or tune the policy on opened regimes. Preserve the conservative invalidate policy in the main simulator.

The protocol was committed first at `17ffba94c8dda88cd7c7fe35bc06a8b5deeadc08`. A new independent version-carrying, FP32-only simulator was committed at `f702784d0f0de041a5d132baa984c23aa2ec61ee`. The results below are from a local execution of that simulator with 32 waves, 64 instructions/wave, four issue slots, 16 RF banks, two RF read ports per bank and 64 cache entries. Each policy sees the same instruction trace.

## Frozen results

| Regime | Policy | Cycles | RF reads | Resident-write demand | Updates granted | Forced invalidations |
|---|---|---:|---:|---:|---:|---:|
| H1 read-mostly | Invalidate | 513 | 64 | 0 | 0 | 0 |
| H1 read-mostly | One-port update | 513 | 64 | 0 | 0 | 0 |
| H2 dependent overwrite | Invalidate | **516** | **2,080** | 1,024 | 0 | 1,024 |
| H2 dependent overwrite | One-port update | **525** | **2,453** | 1,562 | 514 | 1,048 |
| H2 dependent overwrite | Four-port update | 521 | 2,322 | 1,672 | 1,672 | 0 |
| H2 dependent overwrite | Free ideal update | 521 | 2,322 | 1,672 | 1,672 | 0 |
| H3 write-heavy | Invalidate | 1,024 | 2,080 | 2,048 | 0 | 2,048 |
| H3 write-heavy | One-port update | 688 | 1,407 | 2,048 | 688 | 1,360 |
| H3 write-heavy | Four-port update | 513 | 64 | 2,048 | 2,048 | 0 |
| H3 write-heavy | Free ideal update | 513 | 64 | 2,048 | 2,048 | 0 |

**H2 one-port versus invalidate:** RF reads **17.93% worse**, cycles **1.74% worse**. Frozen survival required at least 5% fewer RF reads and no more than 1% cycle regression. Both requirements fail. H1 ties as predicted. H3 has a 32.36% RF-read reduction and 32.81% fewer synthetic cycles, but this is an already-opened workload and cannot override the H2 gate. The zero-capacity control ties across all four policies.

## Physicality and mechanistic interpretation
The version checker rejects stale cached register values. Every resident write is either updated or invalidated; no policy obtains free cache data updates except the explicitly optimistic ideal control. One-port grants at most one update per cycle; four-port grants at most four. Write updates deliberately **do not refresh read-LRU recency**. This is necessary for matching the existing V303 replay, where ideal updates modify resident data without touching LRU order.

For per-cycle resident-write demand `D_t` and `P` update ports, grants are bounded by `min(D_t,P)`; when a write cannot update, its entry must be invalidated. However, `D_t` itself is endogenous to scheduling, eviction and cache policy. The H2 counterexample demonstrates that fewer invalidations need not mean fewer RF reads or fewer cycles. A positive law based solely on write demand and port count is insufficient.

The independent model reproduces the earlier V303 H1/H2 invalidate and ideal-update cycle/RF counts at capacities 0, 8 and 64. Local assertions for zero-capacity equality, conservation, per-cycle port limits and stale-value exclusion passed. Hosted CI should be checked separately after push.

## Evidence tier and limitations
This is a **synthetic issue-simulator falsification**, not matched RTL or a routed electrical result. The model tracks register versions, not numerical FP32 data; only FP32 operations are supported, with no memory-completion coherence or actual cache data-array port timing. It does not price an extra cache update port's area, energy, routing or clock impact. The four-port option is not an equal-resource physical baseline. A simple invalidate control is strictly less hardware-demanding than the one-port candidate; failing the precommitted synthetic gate already justifies stopping physical implementation.

No GPU IPC, tile-level throughput, silicon power, frequency or RTX-5090 equivalence claim follows. Retain all negative results and reproduction scripts in this unmerged branch.

## Reproduction
```sh
python -m research.v303.port_budget > v303_port_budget.json
pytest -q tests/test_v303_port_budget.py
```

The active Vektor mechanism should return to **none** after V303 retirement. A successor must be selected independently from demonstrated bottlenecks, with new prospective tests rather than retuning V303 against these opened regimes.
