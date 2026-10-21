# V266 retirement: matched-control domination (2026-10-21)
Evidence class **E1 only**. No RTL simulation, synthesis, STA, max-cap/slew, energy, or V-Tile integration. V153/V156 remain electrically disqualified.

## Frozen discriminator
The generator was frozen before holdout evaluation: SHA256 32961e9277c3069a430ffb3b06a6a405b5554355dc7c6fe160bae355e663fde9 (the canonical frozen source is in the local evidence archive; this branch contains an equivalent compact generator). Four 1R banks, two word slots/bank, five logical words, exactly one copy/word, C=2 blocked migration cycles, r=0.95 assumed clock retention (NOT measured). Exhaustive capacity-valid static assignments; independent physical-slot/value replay passed all three workloads.

| Workload | Static oracle cycles | Adaptive cycles | Moves | Assumed clock-adjusted gain vs static | Gain vs matched scripted relocation |
|---|---:|---:|---:|---:|---:|
| K5 long phase | 20480 | 12946 | 73 | 1.502858x | **1.000x** |
| Four-hot balanced | 12800 | 12800 | 0 | 0.950000x | **1.000x** |
| Short divergent | 235 | 247 | 0 | 0.903846x | **1.000x** |

**Decisive falsification for this frozen kernel:** the phase list is deterministic. An equal-resource compiler-scripted relocation controller uses the identical migration hardware, metadata, read/write ports and the exact same move sequence; its cycles equal the candidate's exactly. The K5 win over static placement therefore does not establish an architecture mechanism.

**Second validity defect:** each phase repeatedly reads the same four logical words without intervening versioned writes. Conventional operand bypass/collector reuse could suppress many modeled RF accesses. A read-only K5 stream cannot establish GPU-level RF demand. Related prior art: BOW, MICRO 2020, DOI 10.1109/MICRO50266.2020.00084; Memento, ISCA 2024, DOI 10.1109/ISCA59077.2024.00075; CAC, JSA 2024.

## Gates and decisions
- Python functional values, one-copy invariant, no over-capacity, independent replay: PASS.
- RTL proxy: prepared locally, NOT SIMULATED. Icarus/Verilator/Yosys unavailable.
- Free package-index repair attempt: timed out; no second repair attempt.
- Physical matched area, STA, max-cap/slew, 0.5x/1x/2x wire/load: NOT RUN.
- Whole-tile compute/memory/divergent workloads: NOT RUN.
- Power: NOT MEASURED; migration traffic count only.
- **RETIRE V266**, preserve static placement as baseline. No performance, energy, novelty, or RTX 5090-class claim.
- Next sole kernel V267: producer-writeback-triggered rebanking without explicit migration.
