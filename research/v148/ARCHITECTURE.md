# V148 ARCHITECTURE ledger (2026-10-13)
**Retain:** V145 flexible dual RF responses and V146 collector. Low-bit bank mapping remains default pending realistic physical-cost comparison.
**Built:** full-Wave32 collector -> one-deep elastic tagged 24x24 significand multiply. Preserves exact product, product/addend exponents and signs, addend significand, FP classes and lane mask. Two transaction directed HDL test, stalls and tags.
**Not built:** IEEE FMA alignment, addition, normalization, rounding, exceptions, scoreboard, writeback, instruction stream, full tile. This is NOT an FP32 FMA gate PASS.
**PPA:** generic Yosys synthesis of 1- and 4-lane arithmetic plus 1-lane integrated front end is a logic proxy, not physical area, frequency, energy, or full-Wave32 area.
**Target:** Vektor-1A 160 tiles, 2.56 GHz, 128 lanes/tile remain unverified design hypotheses.
**5090-class gates:** all INCONCLUSIVE. No equivalence claim.
**Next decisive action:** connect existing bounded cancellation hardware to an independently checked far/rounding path and verify IEEE edge cases through real RTL retirement.
