# Vektor-097 preregistration (2026-10-11)

Classification: DISCRIMINATION + CAPABILITY-BUILDING.

Hypothesis: V096 recomputes its selected return source during downstream backpressure. A new FINAL head or an age-threshold crossing can change the presented output without a handshake, violating ready/valid stability even when producers obey the hold-until-ready contract.

Prediction P1: a legal two-source trace exposes the instability. P2: sticky-source selection on first stall prevents it in 32,768 exhaustive five-cycle traces and 16,384 deterministic randomized cycles. P3: when downstream is always ready, old and new policies make identical choices. P4: the fix can defer a newly arrived FINAL and does not imply higher GPU throughput.

Controls: same offers/readiness, producer-held data, two and four sources, guard 2/4/16, seed 97/1097/2097/3097. Verify with independent C++ and RTL simulation/synthesis on free CI where available. The repair is established elastic-interface practice, not an architectural novelty claim.
