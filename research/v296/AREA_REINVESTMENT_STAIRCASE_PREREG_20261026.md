# V296 area-reinvestment staircase: preregistered falsification (2026-10-26)

**Scope and provenance.** This is an independent **conditional, equal-budget accounting** experiment using the already-hosted four-way Nangate45 mapped standard-cell areas from run 40244774412, artifact 12618038449. It is NOT a new architecture mechanism, an SRAM-macro estimate, a routed tile area, an achieved performance win, or a replacement for the active paired post-route electrical gate. Preserve all original evidence and prospective GPU holdouts. V296 remains the sole provisional mechanism; V287 is retired.

## Frozen inputs and predictions (before executable evaluation)

- Matched balanced-return RTL mapped area: V296 `A_p=9286.592 um^2`; strongest balanced-return serial `A_s=9844.926 um^2`. Both implement exactly the same priority-greedy admission semantics and 16 banks x 2 read ports.
- Replication thought experiment: a total budget `B=H+N*A_s` for `N` serial slices plus a shared fixed overhead `H`; each candidate copy consumes `A_p`, each serial copy `A_s`. Copies must be independent and all required RF/data/control resources replicated. The **optimistic** copy count is `floor((B-H)/A_i)`. Ignore fragmentation/wire/IO only to obtain an upper-bound opportunity, never a measured implementation.
- Predict **no extra candidate copy** for N=1 and N=16; first possible extra copy at N=17, where the ideal candidate count is 18 versus 17 serial. Predict the threshold formula `N_min=ceil(A_p/(A_s-A_p))` for positive area saving; if `A_p>=A_s`, no finite threshold exists.
- Frozen prospective *conditional win*: N=17, equal physically feasible 3.5 ns clocks, `q=2.992340240625` admitted waves/slice/cycle from the previously checked i.i.d bank model, `b=4` bytes/admission, 100 GB/s **shared** external bandwidth, zero additional control overhead; predict exactly `18/17-1=5.88235%` useful-throughput gain from **one extra physically feasible copy only**.
- Frozen no-win #1: N=1, same clock/traffic/100 GB/s; predict exactly zero gain.
- Frozen no-win #2: N=17 with shared external bandwidth 10 GB/s; predict zero gain even if one more slice fits.
- Sensitivity: vary candidate mapped area up +2% and serial mapped area down -2%, and an adversarial +5%/-5%; report the earliest integer replication threshold or absence. Do not substitute these variations for actual routed PVT/area experiments.
- `T_i=min[n_i*q*f_i/(1+h_i), W/b]` with `f_i` independently measured feasible slice clock (in Hz), `h_i` control overhead, and shared `W` bytes/s. At equal `n,f,h,q`, gain is exactly zero. At arbitrary clock and area, no speedup is allowed until both designs close timing/electrical, are equal-budget, and demonstrate the modeled copy counts. Treat clock/area as optimistic inputs until measured.

## Required falsification checks

Use integer milli-um² arithmetic and exact rational throughput arithmetic. Independently enumerate copy counts for N=1..1000 and verify the first-gain threshold against the closed form; test just below/at/above the threshold; test equal/worse candidate area; verify nonnegative copy counts, shared bandwidth cap, equal-resource equality, and the three frozen win/no-win regimes. Preserve numerical outputs and failed checks. An independent reference implementation must not reuse the threshold formula to determine its result.

**Decision:** This experiment can establish only a precise *area-reinvestment feasibility boundary* and falsify inflated claims that a 5.67% mapped area saving automatically increases a single tile's throughput. If the active detailed-route experiment fails electrical/setup/hold, no physically credible performance claim follows, regardless of this mathematical result. Do not open sealed workload holdouts, merge PR #13, change the mechanism, or touch Kernellum PR #119.
