# V290 retirement — 2026-10-23

**Decision: RETIRE. Evidence E0, not an electrical failure.**

The proposed partial-operand admission is the standard conventional operand-collector transition: each bank independently selects one waiting operand, stores it in the already allocated collector slot and marks the source ready. Both architectures have four slots, two single-read banks, the same operand-ready bits, the same per-bank arbitration and no extra storage. Their state transitions are isomorphic.

Independent implementations using global operand selection versus per-bank queues were tested over all 65,536 two-bank, four-slot, two-operand bank/ready configurations and 10,000 additional arrival-time traces. No differences in completion cycle, per-request completion times or number of RF reads were found. Reproduce with python3 research/v290/equal_budget_checker.py.

The preregistered positive prediction could improve over a deliberately weaker atomic same-cycle read policy, but **not** over the strongest same-budget conventional collector. No distinct hardware mechanism remains to validate. No RTL sim, synthesis, max-cap/slew, STA or power result was obtained; none is claimed.

V287 remains retired by its integrated RF grant bound. Next mechanism must deliberately seek a positive law and freeze both win/no-win predictions before testing.
