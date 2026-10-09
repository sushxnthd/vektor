# Vektor-057 results — 2026-10-09

**All performance counts are deterministic software simulations, not physical GPU IPC.**

| 12,000-cycle BACB synthetic case | Completed | Issued RF reads |
|---|---:|---:|
| FIFO returns, no dedup | 5,332 | 12,000 |
| FIFO returns, dedup | 4,798 | 9,600 |
| Near-completion returns, dedup | 5,332 | 10,667 |
| Four-cycle age-guarded near-completion, dedup | 5,332 | 10,667 |

The selected dedup regression is **-10.015%** and persists at 48,000 cycles (-10.004%). Two return lanes remove it; four collector slots reverse it (+12.49%). These are phase/capacity effects in an abstract collector.

**Prospective prediction audit:** P1–P4 PASS; P5 FAIL (64 randomized probes: 44 wins, 20 ties, zero dedup losses); P6 FAIL (10% identity jitter mean -7.642% vs predicted >=-5%); P7 FAIL (25% jitter mean -4.425% vs predicted >=-1%); P8–P11 PASS (near-done selected +11.13%, 96 unseen periodic patterns: 29 wins, zero losses, 67 ties, mean +1.903%); P12–P14 PASS (age guard completes adversarial first instruction at cycle 9 and retains selected/holdout gain). Predictions were staged and locally SHA256-frozen before the respective experiments; complete preregistration is in the downloadable archive. This branch's summary is a post-experiment record, not a retroactive GitHub preregistration.

**Liveness falsification:** Pure near-done response arbitration leaves the first three-source instruction incomplete after 1,000 cycles in a C+AAAA... stream with eight slots, while FIFO completes it at cycle 6. Age guard completes it at cycle 9.

**Independent replication:** 249 paired initial configurations (498 policy runs), 96 jitter traces (192 runs), 198 priority configurations (792 runs), 98 age-guard configurations (294 runs), and 512 random age-guard configurations, with zero accepted/read/completed counter disagreements. The 512 stress cases had 87 age-guard wins, zero losses, 425 ties against FIFO; zero violations of the conditional ready-response wait bound. They are not independent GPU implementations.

**Limitations:** no register writes, true dependencies, divergence, realistic bank mapping, physical allocation, measured compiled dynamic trace, energy, clock closure or full RTL collector. No novelty or RTX 5090-class claim.

**Next decisive action:** verify selector RTL and equal-budget Yosys synthesis, then integrate age tracking, tags and scoreboard into a multi-slot banked collector.
