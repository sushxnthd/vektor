# V296 prior-art and novelty-bound audit — 2026-10-23

**Scope:** rapid targeted public-literature audit, not exhaustive patent or publication clearance. V296 is the only active architecture mechanism; this document does not introduce a new one.

## Established background that must not be claimed as Vektor inventions

1. **Banked GPU register files, operand collectors, per-bank arbitration and conflict-aware scheduling already exist.** The GPGPU-Sim 3.x architecture manual describes operand collectors, per-bank arbitration, and selecting nonconflicting accesses; it also distinguishes NVIDIA hardware collection from AMD compiler-scheduled bank accesses. Source: https://gpgpu-sim.org/manual/index.php/Main_Page
2. **RF bank conflict reduction by compiler and hierarchical RF management is established.** Sadrosadati et al., *Enabling High-Capacity, Latency-Tolerant, and Highly-Concurrent GPU Register Files via Software/Hardware Cooperation* (2020), includes compile-time register renumbering to reduce RF-bank conflicts. https://arxiv.org/abs/2010.09330
3. **Register access bypass, operand-collector changes and their power/performance tradeoffs are established.** *BOW: Breathing Operand Windows to Exploit Bypassing in GPUs*, MICRO 2020, https://doi.org/10.1109/MICRO50266.2020.00084
4. **Early operand-collector allocation and RF bank utilization improvements are established.** Jeong et al., *Triple-A: Early Operand Collector Allocation for Maximizing GPU Register Bank Utilization*, IEEE Embedded Systems Letters 2024, https://doi.org/10.1109/LES.2023.3307622
5. **Bank-conflict-aware warp scheduling and elastic pipeline ideas are established in shared-memory contexts.** Gou and Gaydadjiev, *Addressing GPU On-Chip Shared Memory Bank Conflicts Using Elastic Pipeline* (2013), https://doi.org/10.1007/s10766-012-0201-1. This addresses shared memory rather than RF, so it is contextual prior art, not an exact anticipation.
6. A broader survey exists: *A Survey of Techniques for Architecting and Managing GPU Register File*, Oak Ridge National Laboratory, https://www.ornl.gov/publication/survey-techniques-architecting-and-managing-gpu-register-file

## Defensible V296 claim at current evidence tier

V296 is a **functionally equivalent implementation topology** for GPU issue-stage RF-bank conflict admission. Its contribution, if it survives post-route verification, is a **specific mapped-and-placed controller area / timing-margin tradeoff against matched original and optimized one-hot RTL controls**, not the invention of RF banking, conflict detection, operand collection, or bank-aware scheduling.

- Preregistered third-round global-route result: nominal **14.066%** controller-area reduction and **+0.40256 ns** modeled setup-slack lead versus strongest controls at 3.5 ns; high-RC **13.746%** and **+0.49882 ns**. Six-case electrical/setup global-route gate passed. Not post-route extracted timing.
- **Same-clock issue-throughput improvement: 0% by functional equivalence.** No observed GPU IPC, FPS, energy, tile-area or operating-frequency gain.
- A lower controller-area implementation is not automatically an architecture-level breakthrough; hardware overhead can be negligible relative to RF, ALUs, caches and crossbars.

## Positive-law boundary, with falsifiable consequences

Let `s` denote controller area saving against a matched control, and `a=A_controller/A_tile` denote the baseline controller fraction of tile area. With unchanged other tile blocks and no extra buffering:

`A_tile,new / A_tile,control = 1 - a*s`.

At nominal global-route `s=0.140662`, `a=0.05` gives a **predicted tile-area saving of 0.7033%**, and a fixed-total-area tile-density factor of `1/(1-a*s) ≈ 1.00708`. These are *conditional accounting identities*, not experimentally validated tile predictions. If `a→0`, the tile-level consequence tends to zero; this is a **predicted no-win regime** even with controller-level improvement. If area is not the binding constraint and both controls meet the same operating clock, expected throughput gain is exactly **0%**. Conversely, a measurable win requires controller area to bind tile packing, or a validated clock/timing/power bottleneck to bind performance.

No claim of a new performance law as a function of compatibility probability, mask overlap, occupancy or bandwidth is justified for V296: it preserves issue decisions and does not change those workload-level rates. Such a law would be required for a different, genuinely throughput-changing mechanism; it must not be retrofitted to V296.

## Critical controls and falsifiers

- **Equal-resource Pareto control:** give the optimized one-hot design the same *tile-level* area, clock, power and wire budget; optimize its sizing and placement independently. Merely applying equal repair steps is necessary but not sufficient for a strongest equal-resource baseline.
- **Physical discriminator:** extracted detailed-route RC, router DRC, setup and pre-CTS hold, then CTS/post-CTS hold, electrical and power closure. The original nominal control's +4.18 ps global-route margin is fragile.
- **Unseen workloads:** freeze area-binding vs non-area-binding regimes, predict throughput/traffic/occupancy before opening holdouts; functional equivalence predicts equal issue traces at equal clock.
- **Novelty check:** search patents and later architecture papers specifically for pairwise RF-bank admission logic and logic-factoring implementations; the present survey is **not** a comprehensive freedom-to-operate or originality determination.

**Research status:** bounded implementation result under investigation. V296 remains provisional. Do not merge or claim RTX 5090 equivalence.
