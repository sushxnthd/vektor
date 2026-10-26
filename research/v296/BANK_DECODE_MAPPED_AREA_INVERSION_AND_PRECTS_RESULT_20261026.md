# V296 symmetric bank-decoder: mapped area inversion and marginal pre-CTS candidate (2026-10-26)

**Decision: the decoder passes the frozen +10% mapped-growth gate, but reverses V296's area advantage. The candidate barely meets the pre-CTS setup guard; matched serial physical timing is still pending. This is not routed electrical closure or a GPU gain.**

## Provenance and evidence tier

Hosted [experiment 40337484954](https://github.com/sushxnthd/vektor/actions/runs/40337484954), four-way mapped artifact 12658617718, independently downloaded and SHA-256 checked: `0cafd08a8a4cbd2164336c9f2ad11e6037c3fac02aa42243ebd1a7641d704ba2`. The [independent mapped checker](bank_decode_mapped_independent_audit.py) reads all four original Yosys/ABC logs, validates the original library digest and source-manifest anchors, checks flop count and topology depth, and rejects a mismatched artifact digest. Its local self-test passed.

Candidate fourth-stage pre-CTS artifact 12659251024, independently downloaded and SHA-256 checked: `c5ec1f863b0cd23cc88fc9f0f468de87a90e1cb1dc0a3698e2af5d872a01cd2c`. This is a **pre-CTS global-route checkpoint with estimated parasitics**, not CTS, detailed route, extracted-RC timing, or signoff. Its serial partner had not completed when these results were frozen.

The intervention replaces a 128-bit variable-shift bank lookup with a shared 32-way equality-masked one-hot decoder and balanced OR tree **symmetrically** in both V296 and serial. Both have the same 388 mapped flops and the same one-extra-cycle operand-capture pipeline. Hosted RTL functional verification passed. The older original routed evidence concerns a different unretimed implementation and must not be subtracted from these numbers.

## Four-way mapped synthesis

| Frozen mapped metric | Retimed V296 baseline | Retimed serial baseline | Decoder V296 | Decoder serial |
|---|---:|---:|---:|---:|
| Nangate45 mapped area (µm²) | 9,519.608 | 9,902.648 | **10,426.402** | **10,143.112** |
| Standard cells | 6,396 | 6,796 | 7,295 | 7,097 |
| Sequential cells | 388 | 388 | 388 | 388 |
| Yosys topological path length (cells) | 247 | 264 | 238 | 280 |

Decoder V296 grows **9.52554%** in mapped area, decoder serial grows **2.42828%**. Both satisfy the preregistered rule rejecting >10% growth. However, V296's baseline **3.86806% mapped area saving** becomes a **2.79293% mapped area *penalty*** with the decoder. V296's topological path shortens by 9 cells; serial's lengthens by 16. **Topological path length is not STA delay and cannot establish a clock advantage.**

## New predictive area-frequency boundary (conditional, no measured clock)

For equal fixed mapped-cell budget equal to `N` decoded serial slices, the optimistic maximum number of decoded V296 copies is

`n_V296(N) = floor(N * 10143.112 / 10426.402) <= N`.

Under identical issue semantics, equal dependency latency, enough independent warps, unlimited shared bandwidth, and physically feasible clocks, a **necessary** frequency ratio for the candidate to exceed serial's ideal aggregate issue throughput is

`f_V296 / f_serial > N / n_V296(N)` (when `n_V296>0`).

For 17 decoded serial copies, only **16** decoded V296 copies fit. Even before bandwidth, scheduling, clock-distribution or wiring penalties, V296 would need a **>6.25% clock uplift** to win this abstract 17-slice budget. At very large `N`, the necessary uplift approaches **>2.79293%**. Shared bandwidth saturation eliminates any benefit from additional clock capacity; this law is not sufficient for realized throughput. The serial fifth-stage control must remain the final physical comparator.

**The earlier 17-serial→18-V296 mapped area-reinvestment hypothesis is falsified for this decoder topology.** This does not kill V296's underlying arbitration mechanism or establish the clock outcome.

## Candidate pre-CTS checkpoint

The original candidate fourth-stage diagnostic reports:
- Intermediate area **16,089.542143 µm²**, zero max-capacitance and max-slew violations.
- Worst setup slack **+0.050206 ns** and hold slack **+0.112877 ns** at the frozen 3.5 ns constraint.
- Setup guard is **+0.050000 ns**, leaving only **0.000206 ns = 0.206 ps** above the guard. This is effectively a zero robustness margin; rounding, physical perturbations and CTS/route may reverse it.
- Critical path remains a long scheduler-to-staged-data path, with multiple inserted buffer chains. It has not demonstrated routed electrical closure.

## Falsification policy and next step

1. **Do not count this as a successful physical repair.** The pre-CTS candidate only marginally passes, the paired serial physical result is outstanding, and the mapped area ordering has inverted.
2. When the serial checkpoint finishes, independently audit both original ZIPs and compare identical stages. Do not conflate pre-CTS with detailed route or mapped with placed area.
3. Only pursue post-CTS extracted-RC implementation if the full matched comparison, including strongest independently optimized serial fifth-stage repair, has a plausible area/frequency/occupancy Pareto win. The candidate must meet setup ≥ +50 ps, hold ≥ 0, zero cap/slew/DRC after routing. Preserve all negative results.
4. A surviving claim must predict an unseen-workload win and no-win boundary with compatibility, bank overlap, port pressure, occupancy, dependency/control overhead, shared bandwidth and feasible clocks. No RTX-5090 equivalence or measured GPU speedup is supported.

V296 remains the sole provisional mechanism, V287 retired, Kernellum PR #119 and prospective holdouts untouched.
