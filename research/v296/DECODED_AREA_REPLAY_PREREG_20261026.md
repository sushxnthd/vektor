# V296 decoded-area matched-budget replay preregistration (2026-10-26)

## Motivation and immutable source evidence

The symmetric bank decoder reverses the retimed V296 mapped area advantage. The original SHA-256-pinned four-way Nangate45 synthesis artifact from hosted run 40337484954 reports decoded serial 10143.112 um2 and decoded pairwise 10426.402 um2 (research/v296/BANK_DECODE_MAPPED_AND_CANDIDATE_PRECTS_RESULTS_20261026.json). At a budget of exactly 17 decoded serial slices, only 16 decoded pairwise slices fit. This falsifies the earlier 17-serial/18-pairwise replication assumption for this decoder topology. This prospective replay is conditional and synthetic, not a substitute for the pending paired serial pre-CTS or routed signoff.

## Frozen hypothesis before evaluation

Compare 17 serial versus 16 pairwise slices under identical 16 banks, two reads/bank/cycle, four issue slots/slice, 2-cycle operand-capture latency, identical warp-indexed request streams, and identical bank-request generation. This isolates the area-replication penalty: the replay intentionally does NOT simulate distinct serial versus pairwise admission logic, so cannot establish a scheduler-efficiency advantage.

Preregistered predicted-no-win: 180 warps, uniform bank traffic, equal clocks. Expect pairwise useful throughput below serial because it has one fewer slice.

Preregistered conditional predicted-win: same 180 warps and streams, candidate clock period 0.90 times serial's, without shared bandwidth cap. Expect clock gain to overcome the one-slice penalty. This is a **hypothetical clock**, not measured or feasible hardware.

Preregistered no-win: same 180 warps and streams, fixed shared memory cap 25 waves per baseline clock interval, period ratio 0.90. Expect both saturated and zero gain. The cap is measured in waves per unit physical time, not cycles, so must be applied AFTER frequency scaling.

Boundary probes: W=32 and W=256 at equal clocks and 0.90 period; 180 warps at period 0.94; 180 warps with hotspot probability 0.8. Seeds 61719 and 61743 frozen, warmup 500 cycles and 4000 measured cycles. All results, including failed signs, must be preserved.

## Model and independent checks

Let q_s(W,h) and q_p(W,h) be replay admissions per local clock at equal resource semantics, and r = T_p/T_s be candidate period ratio. With a fixed external throughput ceiling M in waves per serial-clock interval, the synthetic predicted gain is

G = min(q_p/r, M)/min(q_s, M) - 1.

Without a cap, G>0 iff r<q_p/q_s. Compare the measured replay boundary q_p/q_s with the ideal fully occupied 16/17 ratio, but do not treat 16/17 as a universal bank-constrained law. Check bank-port conservation, per-warp latency, per-slice issue width, area floor, identical streams, and a separately written small-state reference scheduler. Check negative tests that deliberately violate cap-unit handling and area floor.

## Falsification

If a frozen sign fails, preserve it as a falsification. If the decoded serial pre-CTS partner, fifth-stage serial control, or post-route electrical checks erase the candidate's feasible frequency/area advantage, reject the decoder as a winning repair. No real workload holdouts are opened. V296 remains the sole provisional mechanism; V287 stays retired. No RTX-5090 or measured GPU-speed claim.
