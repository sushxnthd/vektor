# V274 retirement: idle-slot RF read-ahead

Decision: **retire V274**. The exploratory RTL lacks pending-fill/occupied-slot suppression and can issue the same speculative read repeatedly. A one-entry repaired version suppresses redundant idle-cycle prefetches, but a conventional ready-lookahead operand collector with the same RF port, slot, tag comparator, scoreboard metadata and read-ahead grant implements the identical mechanism. Thus the incremental mechanism relative to the strongest equal-resource control is zero by construction. This is an architectural equivalence / novelty falsification, not a characterized PPA falsification.

Independent E1 cycle-model check (not RTL simulation): 40 deterministic traces x 2500 cycles = 100,000 collector-state comparisons; repaired candidate vs equal-resource ready-lookahead control mismatches = 0. Six repeated idle hints produce six original speculative reads but only one in the repaired implementation (five redundant in the original). The stress model intentionally does not include backpressure, true instruction retirement or physical RF timing; aggregate read counts are **not throughput or energy results**. It models a single response latency of two cycles and assumes versioned, stable operands.

The V274 frozen unseen positive/no-win workloads were **not opened**. Because the strongest matched lookahead baseline implements the same logic, opening them cannot establish an incremental V274 architectural law.

Physicality: functional equivalence to an established control suffices to retire the candidate. RTL simulation, mapped synthesis, electrical max-cap/slew, STA and macro energy were **not run**. Do not cite V274 as a GPU improvement. No integrated tile change. V153/V156 remain electrically disqualified. No RTX 5090 equivalence claim.

Original source: V274 E0 package (run20). Reproduction: `python3 research/v274/run21_falsifier.py`.
