# V317 register-bank arbitration prior-art boundary (2026-11-01)

This is a **narrow, non-exhaustive** prior-art audit for a rejected scheduler and its strong simple controls. It is not a novelty certificate for a future mechanism.

## Directly relevant GPU register-file research

1. M. Abaie Shoushtary et al., *A Lightweight, Compiler-Assisted Register File Cache for GPGPU* (2023), https://arxiv.org/abs/2310.17501. The Malekeh proposal addresses GPU register-file reads, energy, bank pressure and reuse-aware **dynamic issue scheduling**. It reports reductions in RF reads and RF energy, and a performance improvement in its own evaluated design. These are **authors' reported results**, not reproduced Vektor comparisons. A new Vektor scheduling claim must compare against reuse-aware approaches rather than pretending RF-aware scheduling is new.
2. M. Sadrosadati et al., *Enabling High-Capacity, Latency-Tolerant, and Highly-Concurrent GPU Register Files via Software/Hardware Cooperation* (2020), https://arxiv.org/abs/2010.09330. LTRF combines software-guided RF working-set management with compile-time register renumbering to mitigate bank conflicts. Its physical register hierarchy is not the same as Vektor's simple four-slot RF arbiter; it nevertheless establishes bank-conflict mitigation and compiler/hardware coordination as prior work.

## Related, but not direct register-file baselines

3. C. Gou and G. Gaydadjiev, *Addressing GPU On-Chip Shared Memory Bank Conflicts Using Elastic Pipeline*, International Journal of Parallel Programming 41 (2013), https://doi.org/10.1007/s10766-012-0201-1. Addresses **shared memory**, not RF, and combines conflict-aware scheduling with pipeline decoupling. Do not present its speedups as RF-issue baselines; use it to motivate system-level evaluation rather than isolated grant counts.
4. F. Han et al., *An Access Pattern Based Adaptive Mapping Function for GPGPU Scratchpad Memory*, IEICE Electronics Express 14 (2017), https://doi.org/10.1587/elex.14.20170373. Addresses **scratchpad** bank mapping, not RF arbiter priority. It illustrates why mapping and workload distributions must be controlled.

## Novelty and baseline decision

- Cyclic rotating priority, oldest-first greedy and maximum-cardinality selection are **generic scheduling policies**. No novelty is claimed for them.
- The exact V317 selector fails the frozen completed-work test and requires 5,116 versus 1,321 generic Yosys cells; it is a negative control, not a research contribution.
- The strongest relevant baseline for any future RF proposal should include simple fair scheduling, bank-aware mapping/renumbering where implementable, reuse-aware RF access, and an equal-clock/equal-area design.
- The Vektor four-slot synthetic FIFO model lacks real SASS register-bank mappings, compiler allocation, warp dependencies, operand collectors, instruction issue timing and power. Neither this prior-art note nor synthetic wins establish a GPU architecture result.

**Next:** only a distinct implementable mechanism with a pre-outcome positive boundary, unseen transfer and physical signoff can justify an architecture claim.
