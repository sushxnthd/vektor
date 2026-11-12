# V310 adversarial prior-art audit and strongest-control challenge (2026-10-31)

**Novelty verdict: NOT ESTABLISHED.** The verified duplicate-source register read optimization is a known class of operand reuse. V310's positive early physical screen is not evidence of an original GPU mechanism. Do not market the 1.5625x synthetic admission ratio as a novel GPU speedup.

## Relevant precedents (verify primary publications and scope)

1. **BOW: Breathing Operand Windows to Exploit Bypassing in GPUs**, MICRO 2020, DOI [10.1109/MICRO50266.2020.00084](https://doi.org/10.1109/MICRO50266.2020.00084). The authors explicitly study repeated register operands, RF read bypassing and reducing RF port pressure across instruction windows, reporting an 11% performance improvement in their evaluation. BOW is broader than V310's intra-instruction duplicate check.
2. **CORF: Coalescing Operand Register File for GPUs** (2019), related patent [EP3915009B1](https://patents.google.com/patent/EP3915009B1/en). The work combines operand reads by register packing and bank/sub-bank organization; it is not identical to the V310 implementation, but establishes operand-read coalescing as a known GPU design category.
3. **Memento: An Adaptive, Compiler-Assisted Register File Cache for GPUs**, ISCA 2024, DOI [10.1109/ISCA59077.2024.00075](https://doi.org/10.1109/ISCA59077.2024.00075). A reuse-aware register-file cache and scheduling mechanism is evaluated against GPU workloads. It directly challenges any claim that the correct control is an RF with no operand reuse.
4. **WIR: Warp Instruction Reuse to Minimize Repeated Computations in GPUs** (2017), [publication](https://yonsei.elsevierpure.com/en/publications/wir-warp-instruction-reuse-to-minimize-repeated-computations-in-g/). Warp instruction and physical-register identity reuse is prior art, though its optimization target is broader.
5. **Modern GPU Cores** [technical source summary](https://github.com/imsight-knowhow/npu-design-tutorial/blob/main/notes/modern-gpu-cores/main-note.md) describes register-file cache hits keyed by warp/register/operand position in measured NVIDIA designs, and notes that actual modern NVIDIA RF pipelines need not match a classic operand-collector model. This secondary summary must be checked against the underlying primary study before citing detailed architectural claims.

## Strongest-control impossibility challenge

V310's bank-demand vector is m_i(b) = 1[a_i=b] + (1-d_i)1[b_i=b] for verified same-register d_i. **Any equal-port baseline that already coalesces same-register reads and uses the same fixed-priority admission policy has exactly this demand vector for every input.** Consequently its grants are identical to V310's for every request, not merely on average. Thus the incremental admission gain against that reuse-capable baseline is **exactly 1.0x**, even though V310 can beat the historical no-reuse compact-greedy control on a synthetic workload.

This is a direct analytical equivalence, not an empirical claim that every GPU implements the same policy. The appropriate next control is a practical already-reuse-capable controller and its full comparator/bypass datapath. If this exact policy is the best available strong control, **V310 has no new architecture-level advantage and must be retired as a novel mechanism.** A distinct predictive *measurement* result could still be useful if prospectively validated on real workloads, but that is not a new hardware invention.

## Evidence-tier consequence

- Independent V310 RTL oracle and synthetic issue-law holdouts: PASSED on CI #41166575481.
- Matched Nangate45 controller-only area/placed estimated-RC gate: PASSED on CI #41166647289.
- Equality comparator and data fanout, routed extraction, electrical signoff, real operand distributions, occupancy, memory bandwidth, energy, and strong reuse-capable equal-resource comparison: NOT DONE.
- **Novelty and GPU performance: NOT ESTABLISHED.**

**Decision:** retain V310 only as a bounded calibration/physical-control experiment pending the strong-control gate. Do not promote to world-class architecture mechanism, and kill the performance/novelty claim if the practical reuse-capable control is equivalent. Preserve V309's physical no-go and all negative controls.
