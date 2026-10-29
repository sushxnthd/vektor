# V309: external-PTX bottleneck qualification (frozen before implementation)

Date: 2026-10-29. Branch: `research/v309-external-ptx-bottleneck-gate`.

## Scientific status
**No V309 hardware mechanism is promoted.** V287/V296/V297/V298/V301–V308 remain retired as documented in their closed unmerged PRs. This PR is a *qualification experiment* to replace synthetic-only candidate generation with external compiler-produced workload evidence. It must not be described as a physical GPU win.

## Immutable upstream inputs
1. Stanford CS336 Triton GELU, generated LLVM NVPTX, commit `de53a9f979a6ee35f7d13a5e1aadee5ea1afc58e`, `var/triton_gelu-ptx.txt`, Git blob `09d8fce9016b6fe0e36e31ac3a47fc9feddee206`. Target `sm_100a`.
2. parallel101 CUDA atomic reduction, generated NVVM PTX, commit `aa7715d26b55bda8ad7a9444a923c916eda30b7f`, `08/07_atomic/04/a.ptx`, Git blob `17873acef2f5137137ca0c4967bd696b97e31c01`. Target `sm_52`.

Pinned GitHub raw URLs, not third-party source copies, will be used. These kernels have already been visually inspected, so they are **exploratory external cases, not unseen prospective holdouts**. Different targets are not hardware-matched.

## Questions, model and kill gates
- Parse instruction mnemonics, explicit register source uses, unique source registers, branch/predicate uses, memory operations and duplicate-source broadcast opportunities from PTX text. Exclude special registers, constants, comments and debug sections. Handle vector operands and predication.
- Compare a *naive* per-occurrence RF read count against the strongest free intra-instruction duplicate-source broadcast baseline. A duplicate source within one instruction may require only one read, so do **not** claim its removal is a novel hardware mechanism.
- Lower bound on scalar register read service with `B` banks and `P` reads per bank: `cycles >= ceil(total_unique_explicit_reads/(B*P))`. This is an **optimistic aggregate bound** ignoring bank conflicts, dependency stalls, control flow, bypass, memory and execution units. It is not a throughput prediction.
- For the two external kernels, report raw counts, static instruction mix, source reuse and the bound for (B,P)=(2,1),(4,1),(8,1). No measured runtime or physical bank layout is inferred.
- Fail closed if either source changes its Git blob hash, parsing finds zero instructions, or malformed instructions are silently dropped. Unsupported PTX constructs must be counted and disclosed.
- **Hardware promotion gate:** requires >=3 independent workload families, SASS/dynamic traces or an experimentally validated PTX-to-physical mapping, a measured bottleneck, a resource-matched strong control, a frozen unseen workload win/no-win, and an implementable mechanism with RTL/synthesis/physical gates. Static PTX alone cannot satisfy this.
- Independent checker must test destination/source separation, predicated reads, duplicate operands, vector registers, special registers and malformed input; an intentional mutant must fail.

## Decision
If PTX static evidence cannot establish a measurable resource bottleneck, keep V309 as a negative qualification result and do not invent a scheduler, cache or GPU-speedup claim. Next step is obtaining real SASS/trace/performance-counter evidence, not tuning a new synthetic queue. No modification of Kernellum PR #119.
