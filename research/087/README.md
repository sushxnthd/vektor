# Vektor-087: conditional writeback fairness

Base: research/wb-calendar-086 at 126abfc973180a5ed8fdaadf0472ee587209a58c. Date: 2026-10-10.

DISCRIMINATION: A per-(bank,latency) rotating client pointer is predicted to fix the Vektor-086 fixed-priority starvation in a homogeneous request class. Python simulation: fixed priority [1000,0,0,0] versus rotating [250,250,250,250] for 1000 continuous same-bank same-latency requests. Residual against prediction: zero.

SURPRISE: Cross-latency prebooking defeats per-class fairness. For two persistent clients with latencies [1,2], rotating simulation produced [1,1000] grants. Swapping latencies swaps the winner. Explanation: latency-2 reservations capture future deadlines before latency-1 requests arrive. This FALSIFIES global fairness claims; conditional same-class fairness survives.

CAPABILITY-BUILDING: Independent C++17 event-calendar replication matched 4096 and 2048 Python-generated cycles (12288 grant/due comparisons). Both are software models, not RTL validation. Equal-input aggregate reservation totals matched the fixed-priority baseline in these two runs. 12.5% of generated vectors were minimally guided probes.

World model:
- KNOWN (software): fixed-priority starvation; conditional homogeneous RR fairness.
- BELIEVED: future-deadline prebooking causes cross-latency starvation.
- FALSIFIED: per-class RR guarantees global fairness.
- ANOMALOUS: same aggregate reservations with dramatically different client service.
- CONFLICTING: reservation grant fairness is not architectural completion correctness.
- UNTESTED: RTL safety and fairness, area/timing/power, cancellation, value-aware WAW, full GPU performance.

Prediction before RTL CI: oracle equivalence in 4096 and 2048 cycles; rotating arbitration will require more generic synthesis cells than Vektor-086's reported 694. Neither claim is established until CI finishes.

Prior-art audit: round-robin arbitration and reservation calendars are standard mechanisms; no novelty claimed. RTX 5090-class gates (compute, tensor, memory, graphics, ray, PPA, KPX software) remain INCONCLUSIVE. Official external reference: https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/ .

Single next decisive experiment: compare deadline-owner guard slots against per-class RR at equal hardware budget, then add cancellation/generation tags and value-aware verification. Personal spend $0.

## RTL verification and synthesis evidence (2026-10-10)

All steps passed on two free GitHub Actions runs (Yosys 0.33, identical generic synthesis command). Baseline rotating implementation: https://github.com/sushxnthd/vektor/actions/runs/38061208844 . Static-index two-pass optimization: https://github.com/sushxnthd/vektor/actions/runs/38061331996 .

- Both variants: 4096 default and 2048 two-port RTL cycles matched independent Python oracle; C++ independently replicated 6144 cycles (12288 grant/due comparisons).
- Both variants: bounded 6-step bank-capacity and pointer safety SAT proofs passed from zero-initialized state. These are NOT unbounded proofs.
- Generic Yosys cell count: Vektor-086 fixed priority 694 (earlier same-flow report), 087 dynamic-index RR 5711, 087 static-index RR 2903. Static-index optimization reduced generic cells 49.17% against the equivalent 087 dynamic-index implementation, but remains 4.18x the Vektor-086 fixed-priority cell count. These are NOT mapped area, timing or power measurements.
- Same-latency fairness was verified in software. The cross-latency starvation counterexample survives RTL equivalence: this controller is NOT globally fair.

### Scaling law and equal-budget tradeoff

For two continuous requesters with fixed latencies a<b, one bank and one write port, predicted shorter-client startup grants = b-a; longer-client grants = 1000 in a 1000-cycle run. All ten held-out pairs 1<=a<b<=5 matched (zero residual). Conditional synthetic law only, no novelty claim.

A strict deadline-owner guard gave [2503,2500,2500,2500] reservations in the 10000-cycle heterogeneous case versus RR [1,1,1,10000], but cost utilization: one active client 2500 versus 10000; random 55%-valid requests 6456 versus 9101 (29.1% fewer). This tradeoff argues against unconditional strict ownership. Source: experiments/deadline_guard_probe_087.py.

**Architectural decision:** keep static-index RR as the cheaper *conditional fairness* reference, not a canonical globally fair scheduler. Elevate cross-latency deadline admission as a first-class bottleneck. Next: deadline-aware fairness with low utilization cost, then cancellation and value-aware verification. RTX 5090-class gates remain INCONCLUSIVE.
