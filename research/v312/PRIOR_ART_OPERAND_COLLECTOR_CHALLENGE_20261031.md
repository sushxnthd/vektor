# V312 prior-art and architecture-model challenge (2026-10-31)

## Established mechanisms
- [GPGPU-Sim 3.x manual: register access and operand collector](https://gpgpu-sim.org/manual/index.php/Main_Page) describes a buffered operand collector with per-bank request arbitration. The scheduler need not reject an entire warp simply because two register reads cannot be served in one cycle. Collector units hold partial operands and spread reads over cycles. This is a **stronger architectural control** than the V312 immediate-issue model.
- [GPGPU-Sim operand collector source](https://github.com/gpgpu-sim/gpgpu-sim_distribution) implements `opndcoll_rfu_t` with collector allocation, read arbitration, and ready dispatch. A correct comparison must reproduce buffering and arbitration rather than comparing only immediate same-cycle grants.
- [RLWS (Anantpur et al., 2017)](https://arxiv.org/abs/1712.04303) and numerous earlier warp-scheduling techniques adapt candidate selection to resource stalls. Multi-candidate selection and backup warps are not, by themselves, novel.
- [A Variable Warp Size Architecture (ISCA 2015)](https://engineering.purdue.edu/tgrogers/publication/rogers-isca-2015/) demonstrates prior work on reconfiguring warp scheduling and ganging. It is adjacent, not the same mechanism.

## Decisive physical-model mismatch
The V312 16-bank, two-read-port, four-slot synthetic model assumes both operands must be available **in the same cycle** to admit an instruction. Realistic operand collectors may accept an instruction into a buffer and complete its operands over multiple cycles. Under such decoupling, immediate-grant gains can be converted into **zero incremental sustained throughput** if the collector and bank ports are the actual bottleneck.

The V-Tile code currently has a tightly coupled scheduler/RF admission path; the V312 result is a credible test of that *particular toy issue-control interface*, but cannot be generalized to NVIDIA SMs or a modern full GPU.

## Required strong-control kill experiment
Construct a fixed-capacity operand collector with a bank-read queue and the same four-slot issue and 16x2 bank-port resources. Compare:
1. existing head-only + collector buffering;
2. V312 fallback + identical collector buffering;
3. a strong reuse-aware, bank-aware two-choice scheduler + identical collector buffering.

Match collector depth, ready waves, read arbitration, occupancy, issue width, register IDs, datapath and clock constraints. Freeze conflict-burst and disjoint no-win workloads before collecting performance. If strong collector buffering removes V312's incremental gain or its timing/area overhead dominates, retire V312 without further optimism.

## Claim boundary
The source-pinned 1.9497x hotspot and 1.2674x transfer results are **synthetic same-cycle admissions**, not cycle-level instruction retirement or GPU throughput. Even the physically factored RTL only establishes correct combinational selection and generic cell mapping. The architecture novelty and practical performance hypotheses remain unproven.
