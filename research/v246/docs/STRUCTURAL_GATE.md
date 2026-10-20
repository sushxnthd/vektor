# V246 structural discriminator — 2026-10-20

Evidence class: executable structural model, NOT physical PPA. Frozen positive seed 246101, negative seed 246102. Reproducibility: `python3 research/v246/sim/structural_gate.py`.

For 8 logical register names × 8 four-lane groups, each physical group stores 128 data bits. With 128 physical group slots, a direct runtime mapping table needs 64 × 7-bit pointers plus 64 valid bits = 512 bits = 4 group-equivalents per warp, BEFORE free-list, wires, crossbar, and port overhead. The original h=2 assumption is not justified for this direct-map RTL.

The positive synthetic trace has peak live groups 29/64 and all eight logical register names live. Whole-register virtualization needs 64 groups/warp and admits at most 2 warps at C=128; the direct-map candidate needs 29+4=33 and admits at most 3; static compiler subgroup interval coloring needs exactly 29 and admits at most 4, using the same data-port budget but without runtime mapping. Thus the frozen positive prediction of four candidate warps fails for this implementation, and no incremental gain over the strongest static subgroup-coloring control is shown. The negative trace has 64 live groups: whole-register control 2, candidate 1, static coloring 2.

For straight-line, compile-time-known group lifetimes, interval graph coloring requires exactly the maximum simultaneous live group count. Tested both frozen traces, 1024 random 64-interval traces, and 240 independent exhaustive-coloring instances. This result DOES NOT establish dominance under path-dependent liveness or runtime-varying cross-warp phases. The subgroup-colored control may increase instruction address bits; this was not physically measured.

Physicality gate: functional interval-model check passed; RTL source prepared locally but connector rejected its publication; RTL simulation, synthesis, max-cap/slew, matched STA, energy, wire/load sensitivity NOT RUN. No integrated tile change. V153/V156 remain electrically disqualified.

Next gate: identify a path-dependent, compiler-safe regime where runtime subgroup allocation wins against both static subgroup coloring and whole-register virtualization with realistic metadata and reserve. No more than one further V246 run before retirement/pivot if physical qualification remains absent.

Prior art: GPU Register File Virtualization (MICRO 2015); Software-Directed Techniques for Improved GPU Register File Utilization (TACO 2018); GREENER (2017); Warped-Compression (ISCA 2015). Novelty unestablished.

Publication failure: attempted `research/v246/rtl/group_rf_min.sv` via GitHub connector; rejected by safety checks. Full local source and results preserved in V246 evidence ZIP.
