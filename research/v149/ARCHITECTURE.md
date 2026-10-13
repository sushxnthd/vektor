# V149 ARCHITECTURE ledger: Wave32 FP32 cancellation path

**Changed block:** V146 Wave32 RF collector -> V148 exact 24x24 significand multiplication -> V149 bounded 49-bit cancellation accumulator + RNE packer, with elastic ready/valid, tags, masks and per-lane support.

**Real capability:** for supported finite opposite-sign close cases, this RTL candidate computes correctly rounded binary32 FMA outputs and IEEE NX/UF/OF flags. A complete IEEE-754 FMA has NOT been built; unsupported lanes require a FAR/special datapath and must not retire.

**Controls:** same RF port count, collector, multiplier, masks and output buffering as V148. Generic close packer synthesis alone is not an equal-resource Pareto result.

**Next:** run CI and preserve raw outputs; fix any HDL failures. Then build far/special path and merge with close stage, implement per-register scoreboard/writeback, and run KPX vector FMA/reduction/GEMM with realistic backpressure. Compare general vs specialized finishers at equal area/ports.

**RTX 5090 reference:** full FP32 execution gate FAIL/incomplete; matrix, memory, software, physical PPA, graphics and ray INCONCLUSIVE. No equivalence claim. Zero personal spend.

## Architecture pivot (frozen workload probe)

CLOSE-eligible fractions were 0% positive vector, 12.72% synthetic GEMM, 26.36% signed vector and 25.39% divergent active lanes; cancellation-only control was 100%. Therefore Vektor must implement FAR/special arithmetic as its default complete FMA path. The bounded CLOSE packer may remain a selective optimization only if its additional area, timing and selection logic are justified by equal-budget workload throughput/energy. Do not treat 5708 generic CLOSE cells as a winning GPU architecture.
