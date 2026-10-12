# Vektor-125 — KPX-0 Wave32 integer RTL candidate

**Evidence status:** independent local software checks pass; RTL simulation and synthesis have not yet run. This is not an NVIDIA implementation or a complete GPU.

## Implemented scope

Original Wave32 integer/predication SystemVerilog module, vector-driven testbench, 224 deterministic programs, source-pinned V124 Python/C++ reference interpreters, a new independent step model, preregistration, world model and RTX 5090 target ledger.

| opcode | number | behavior |
|---|---:|---|
| laneid | 0 | active lane index |
| imm | 1 | uint32 immediate |
| add/mul/xor | 2/3/4 | lane-local modulo-2^32 arithmetic |
| iflt | 5 | unsigned comparison and mask-stack push |
| else/endif | 6/7 | alternate path / restore parent mask |
| ballot | 8 | active nonzero-lane bitmap |
| reduce_add | 9 | modulo-2^32 active-lane sum |

The RTL intentionally omits memory, FP32, tensor/matrix, graphics, ray tracing, caches and NoC. The behavioral 16 x 32 x 32-bit register array and 32-wide arithmetic datapaths have not been physically characterized.

## Reproduce

From the repository root on a system with Python 3, C++17 compiler, Icarus Verilog and optionally Yosys:

1. Compile `research/125/replica_v124.cpp` using `g++ -std=c++17 -O2` into `/tmp/vektor125-replica`.
2. Run `python3 research/125/generate.py --replica /tmp/vektor125-replica`.
3. Compile `research/125/kpx_wave32_int.sv` and `research/125/tb_kpx_wave32.sv` with `iverilog -g2012 -s tb_kpx_wave32` into `/tmp/vektor125-rtl`.
4. Run `vvp /tmp/vektor125-rtl` from the repository root. Expected successful message starts with `V125 RTL PASS`. **This message has not yet been observed.**
5. Optionally run Yosys `read_verilog -sv`, `hierarchy -check`, `proc`, `opt`, `check`, and `stat`. Generic synthesis does not establish 2.56 GHz, area, or power.

The complete local evidence archive also contains a convenience `reproduce.sh` and proposed GitHub Actions workflow, but repository-tool safety checks prevented uploading those two files. The repository's existing RTL CI checks older scheduler blocks, not V125.

## Measured outcomes and limitations

Locally executed **software only**: 224/224 model agreement, 4,945 instructions, 28/224 (12.5%) minimally guided probes, 139,189 generated RTL comparison checks. No RTL execution, gate-level synthesis, PPA, GPU performance, or RTX 5090-class evidence has been established.

**Next decisive action:** run Icarus differential RTL verification; minimize any mismatches before synthesis and architectural integration.
