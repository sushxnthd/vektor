# V151 ARCHITECTURE ledger

Block: 64-bit leading-aligned signed-tail FP32 finisher, same interface as the V150 exact-wide reference.

Decision under test: substitute a bounded general finisher after the Wave32 significand multiplier. This is a correctness and generic-synthesis experiment, not a new scheduling policy.

Current gates:
- V148 collector and multiplier: previously verified independently.
- V150 full-range standalone reference: verified.
- V151 bounded finisher: PASS, 24,220/24,220 RTL vectors; 14,459 generic cells and 383 generic logic levels.
- Full Wave32 collector->multiplier->bounded-FMA directed gate: PASS, 5 transactions. Scoreboard and architectural writeback: open.
- Mapped timing, physical area, power, tensor, memory, compiler and complete GPU: open.

Negative control: fixed-bank response routing was rejected in V145. This experiment does not revisit that result.

Wildcard: near-cancellation of a wide product against a narrower addend is an important width-boundary adversarial case.

Scientific novelty: not established. No GPU performance equivalence is claimed.
