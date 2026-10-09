# Vektor-057 verified selector RTL — 2026-10-09

Commit: `2f28cf26b6a172dbfaffe0cc44630555c1667693`.
GitHub Actions: https://github.com/sushxnthd/vektor/actions/runs/37896833063 (SUCCESS).

| Return selector (8 entries, 2-bit remaining, 6-bit age) | Yosys generic cells | Differential RTL vectors |
|---|---:|---:|
| FIFO | 73 | 4,096 PASS |
| Nearest completion | 172 | 4,096 PASS |
| Maximum-age urgent override | 546 | 4,096 PASS |
| FIFO-first urgent override | **277** | 4,096 PASS |

Additional 4,096 monotonic-age vectors passed through the maximum-age RTL, making 20,480 RTL comparisons total. Python independently checked 4,096 structural-equivalence vectors. **P15 PASS, P16 PASS:** first-urgent uses **49.27% fewer generic cells** than max-age on the same commit and synthesis flow. Initial max-age prototype used 551 cells on prior commit; use 546 for equal-budget comparison.

**Mechanism:** If queue entries are in FIFO arrival order and response ages are non-increasing, the first urgent response is necessarily a maximum-age urgent response. Therefore a first-match urgent scan is equivalent to max-age priority under this invariant. Without the invariant the policies differ (entry0 age4, entry1 age9).

**Boundaries:** The selector is combinational only; it does not implement queue ordering, age updates, operand tags, return datapath, or scoreboard. Generic cells are not mapped area or timing; physical power, frequency, and GPU-level speedup are UNTESTED. No novelty claim.

**Next:** prove FIFO/age-order invariant in a tagged collector and run mapped timing and area.
