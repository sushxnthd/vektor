# V296 detailed-route compatibility amendment — 2026-10-23 (before rerun)

**Preserve original failure.** The first detailed-route run [39982355576](https://github.com/sushxnthd/vektor/actions/runs/39982355576) stopped at **original/nominal** with `[ERROR DRT-0305] Net one_ of signal type POWER is not routable by TritonRoute. Move to special nets.` No V296/optimized detailed route or extracted SPEF completed; this is **not** evidence for or against V296's physical PPA. [13-file raw failure artifact 12514132485](https://github.com/sushxnthd/vektor/actions/runs/39982355576/artifacts/12514132485).

The pinned Yosys flow writes constant supply nets without explicit technology tie-cell drivers. OpenROAD's detailed router rejects such unspecialized POWER nets. Prior OpenROAD maintainer guidance recommends Yosys `hilomap` to map constants to technology tie cells: https://github.com/The-OpenROAD-Project/OpenROAD/discussions/5168

**Prospectively declared compatibility correction:** append the identical Yosys command `hilomap -hicell LOGIC1_X1 Z -locell LOGIC0_X1 Z` after `abc -liberty` and before `clean; check; write_verilog` in **all three** original, optimized and V296 synthesis variants. Existing `repair_tie_fanout` applies equally. Keep RTL, timing constraints, clock, RC model, routing parameters, pass count and all frozen physical acceptance predicates unchanged. Do not mark power nets as ordinary SIGNAL merely to bypass routing, and do not ignore the DRT error.

**Comparability warning:** this creates newly synthesized netlists and thus is a **separate, explicitly amended detailed-route experiment**; previous third-round global-route results remain valid only for their original netlists and must not be silently treated as identical physical implementations. Compare all six within the amended run. Retain the original failure and all new negative results.

This is the single compatibility-repair allowance, not permission to tune constraints or remove physical gates. If this does not resolve DRT-0305, preserve the new failure and diagnose before further experiments. V296 remains sole provisional mechanism; holdouts sealed.
