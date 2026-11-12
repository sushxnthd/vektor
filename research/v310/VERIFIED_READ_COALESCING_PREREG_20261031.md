# V310 preregistration: verified duplicate-operand RF read coalescing (2026-10-31)

**Status at freeze: protocol only. No V310 RTL, synthesis, timing, workload outcomes, or holdout observations have been evaluated.** This is a new candidate after the physically rejected V309 exact-max implementation, not a resurrection of V287/V296/V309. V309's draft PR #26 remains an immutable negative-result record.

## One mechanism and causal assumption

Four request slots, sixteen RF banks, **two read ports per bank**. Each request nominally requires two source reads. If and only if the producer/rename/scoreboard path supplies a *verified equality of the complete physical register identities* for both operands of one request, the RF can read that word once and fan it out to both operand consumers. Bank equality alone is NOT sufficient: distinct registers may map to the same bank. The RTL receives a trusted one-bit duplicate_verified per request and defensively ignores it when the two bank indices disagree. A complete tile implementation must supply the equality comparator, register-ID timing, operand duplication datapath and correct stall/forwarding behavior; this controller alone does not implement those blocks.

The **strong baseline** is the compact four-slot fixed-priority greedy controller from V309 (251.370 Nangate45 area units in that earlier experiment), retaining two reads even when two operands use the same bank. This is a valid *existing Vektor RTL* baseline, not a claim about actual GPU hardware: real GPUs may already coalesce identical-register reads. A second stronger control must include equality and forwarding logic in both designs before any hardware novelty or net-power claim.

## Frozen prediction / no-win and win

For **exactly two active requests**, both operands of each request assigned to one shared bank, and independent verified-duplicate indicators with probability q, baseline admits exactly one request. The coalescer admits two if and only if both indicators are true. Therefore the *exact expected issue-admission ratio* is

    R_issue(q) = 1 + q^2.

Prospective win: q = 3/4 -> **R_issue = 25/16 = 1.5625**.
Prospective no-win: q = 0 -> **R_issue = 1** (bitwise baseline-equivalent).
Unseen law checks after implementation: q = 2/5 -> **29/25 = 1.16** and q = 9/10 -> **181/100 = 1.81**. Freeze these values now, before evaluating them. Independent random seeds: 31031 (win), 31032 (no-win), 31033 and 31034 (unseen); 100,000 opportunities per regime, report binomial sampling error and use tolerance 0.01 in issue ratio. Include an adversarial bank-equal/register-different control, q=0 with identical bank IDs.

These are deliberately *synthetic admission* predictions. No GPU throughput improvement follows without demonstrating real verified-duplicate frequency and a downstream bottleneck.

## Physical / system kill gates

1. Independent 4-slot per-bank counting oracle, deterministic exhaustive reduced-bank cases, invalid flags, and adversarial controls. Both the new controller and the copied optimized greedy baseline must be verified.
2. Same Nangate45 standard-cell library and Yosys/OpenROAD version, matched constraints and geometries, **same-netlist zero-wire timing control** plus two placed-RC floorplans; report area, worst delay, slew, capacitance, fanout, wire/load sensitivity. No reuse of incomparable prelayout timing from V309.
3. Frozen preliminary ceiling: controller mapped area <= 1.50x compact greedy. For the two-slot q=0.75 motif under an explicitly *clock-limited* model, reject if candidate/base placed delay >= 1.5625x; for an empirically observed real-workload issue gain G, reject if delay ratio >= G. No-win q=0 must not be sold as an improvement. Even a passing gate does not imply GPU throughput.
4. Measure equality-comparator/forwarding mux and RF-port electrical load; include them in matched tile-level area, timing and power proxies. If their cost erases the gain, kill V310.
5. Freeze a real-workload prediction before inspecting its outcome; measure verified identical-register operands, bank overlap, port contention, occupancy, issue stalls and memory bandwidth. Compare to a baseline that already has the strongest practical operand reuse, not just the historical Vektor arbiter. If the strong control removes the benefit, kill the novelty/performance claim.

## General boundary, beyond the two-request identity

For a request i and bank b, with source banks a_i,b_i and trusted duplicate d_i, the exact per-request demand is

    m_i(b) = 1[a_i=b] + (1-d_i) 1[b_i=b].

Greedy admission is the deterministic sequential capacity-2 decision over these demands. For any prospectively specified joint distribution D over valid masks, bank indices and duplicate flags, compute E_D[A_coalesced] / E_D[A_baseline] *before* measuring outcomes. Physical clock, occupancy, bandwidth, control and bypass overhead are separate penalties, not implicit in admission gain. In a clock-limited, issue-bound approximation, a necessary win condition is G_issue > D_placed, where D_placed = delay_new / delay_base; it is not sufficient when other bottlenecks bind.

## Novelty and evidence discipline

Same-register operand reuse, RF port sharing and bank-conflict mitigation are prior-art categories; no novelty is claimed without an audit. The possible contribution is a measured, prospective physical boundary for this specific Vektor tile. Preserve all negative results, source/tool identities and raw artifacts. This PR is research-only, draft, and never auto-merged. Kernellum work remains isolated in its own repo/PR.
