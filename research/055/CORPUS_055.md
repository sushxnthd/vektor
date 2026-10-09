# Vektor-055 pinned public PTX corpus

**Hand-authored application PTX:** Tugbars/Bootstrap-Particle-Filter-in-PTX, path `gpu_bpf/ptx_assembly/bpf_kernels_full.ptx`, commit `25537f2beb63088129291f9e557997c59f2a5838`, blob `87d142cda1b01f85c7593418957081a5cd3e69e9`, GPL-3.0. Contains 14 analyzed kernel entry points in this revision. https://github.com/Tugbars/Bootstrap-Particle-Filter-in-PTX

**Compiler-produced control:** craton-co/craton-tensor-wasm, path `kernels/vector_add.ptx`, commit `81844a87dcb4083ffc85efc9cfabfe9f05c98c35`, blob `0a36fcc2eb96ffdea89a4f0d393fb60555601048`. https://github.com/craton-co/craton-tensor-wasm

The corpus is **not vendored** into Vektor; the audit fetches upstream files at pinned commits and checks git blob identity. Static arithmetic/logic instructions from a fixed opcode allowlist with at least two explicit register-valued source operands are counted. Destination, immediates, memory operations, tensor ops, and special control instructions are excluded. No dynamic instruction frequency, physical register allocation, SASS, graphics, ray or memory benchmark is inferred.

BPF: 242 distinct two-register-source, 10 aliased two-register-source, 20 distinct three-register-source eligible instructions. Compiled vector-add: 5 distinct two-source and 1 distinct three-source. Combined static-uniform proxy: **247 distinct two-source, 10 aliased two-source, 21 distinct three-source** instructions. This proxy is not representative of general applications.

Prior art: operand reuse and bank-aware collection already exist in GPU research and open simulation, including GPGPU-Sim; no architectural novelty is claimed.
