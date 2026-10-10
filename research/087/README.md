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
