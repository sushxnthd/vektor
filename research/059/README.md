# Vektor-059: Response identity and protocol integrity

Date: 2026-10-09. Parent: Vektor-058, commit `4575cf311b7fe8373c091cfc2a8d178ee4a6db45`.

**Model-only replication:** 10,080 original vectors and 216,000 new Python semantic-model/independent-oracle cycles agree (288 configurations, 12.5% minimally guided probes). A separately implemented C++ oracle agrees with 43,200 new cycles. These are **not** executed Verilog simulations.

**Structural counterexample:** If the return fabric uses an instruction-only 8-bit tag, two out-of-order operand returns for one instruction are indistinguishable without an operand slot. Under an explicitly hypothetical 32 waves × 8 outstanding instructions/wave × 3 operand responses/instruction envelope, there are 768 concurrent response identities. A 10-bit globally unique response ID (5 wave + 3 instruction slot + 2 operand bits) suffices under bounded concurrency; 8 bits do not. Epochs are needed only subject to a specified reuse/stale-return protocol. This is an integration requirement, not a new hardware invention.

**Outstanding:** Actual Icarus RTL simulation, Yosys synthesis, temporal formal verification, real GPU workloads, and chip-level performance/area/power. The user-supplied Vektor-058 RTL is not yet committed to this branch. Full reproducibility package exists outside the repository.

**Next action:** Commit RTL and parameterized testbench, run free CI, then integrate an operand-indexed scoreboard with explicit tag-allocation and release contracts.

**RTX 5090-class:** INCONCLUSIVE in all physical capability gates.
