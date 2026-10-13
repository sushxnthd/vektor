# V154 ARCHITECTURE

Affected block: Vektor Wave32 FP32 FMA finisher, post multiplier and operand collector.

Retain V151 as functional reference. V153 two-stage cutset has passed 24,220 oracle vectors with elastic tag/mask ordering but is NOT promoted as the implementation baseline until synthesis and matched physical feasibility.

V154 synthesizes V151 and both V153 combinational stages using the same Yosys script. Record generic cell count and longest path; compare maximum stage depth, but do not sum cell counts as a silicon area estimate. Additional 138 interstage register bits per lane require accounting.

If synthesis confirms shorter paths, next integrate scoreboard and architectural writeback, map to open liberty with matched buffering, then measure dependency-heavy, independent, memory-bound and divergent kernel throughput. If no improvement, kill/reformulate the cutset and retain V151.

Scientific mechanism remains conventional retiming, not novelty. RTX 5090-class capability unestablished.
