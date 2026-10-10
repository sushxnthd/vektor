# Vektor-081 preregistration

**Class:** DISCRIMINATION / CAPABILITY-BUILDING. This milestone validates a finite, backpressure-aware RF operand collector, not GPU throughput.

**H1:** Under a stable wave-register snapshot, each accepted source request produces exactly one latched operand; no operand is skipped or duplicated, regardless of request/response stalls. Expected: zero errors in directed and seeded tests.

**H2:** A collector which accepts untagged stale RF responses after cancellation/reset can attribute old data to a new instruction. Expected: an explicit adversarial counterexample; no claim of reset safety without downstream drain or tagged response identity.

**H3:** A finite source buffer permits forward progress under fair RF grant and response assumptions; without fairness, bounded liveness cannot be asserted. Expected: no stalls with a permanently responsive RF, and a watchdog timeout when response never arrives.

**H4:** Resource model consistency: one-outstanding-read collection never exceeds one RF request/cycle and incurs at least source_count accepted read requests per instruction when no cache/bypass exists.

**Controls:** Fixed instructions, data, seeds, RF timing patterns; compare Python reference and SystemVerilog where tool execution is available. Keep RTL synthesis separate from timing, power and area claims. Freeze hypotheses before examining results.
