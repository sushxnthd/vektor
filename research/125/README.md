# Vektor-125 — KPX-0 Wave32 integer RTL slice

This is a **new original RTL module**, not a NVIDIA implementation. It follows the KPX-0 integer/predication contract introduced in V124, and deliberately excludes memory instructions, FP32, matrices, graphics, ray tracing, caches, or NoC.

## Run

On Ubuntu with `g++`, `python3`, and `iverilog`/`vvp` installed:

```bash
bash research/125/reproduce.sh
```

The script builds an independently written C++ reference, generates 224 deterministic programs, verifies them against the V124 Python reference and a new step model, then compiles and simulates RTL. Generated `vectors.txt`, `local_results.json`, and `rtl_results.log` are evidence outputs, not prerequisites for CI.

## ISA slice encoding

| op | number | semantics |
|---|---:|---|
| laneid | 0 | active lane receives lane index |
| imm | 1 | active lane receives uint32 immediate |
| add/mul/xor | 2/3/4 | uint32 lane-local operations |
| iflt | 5 | unsigned per-lane comparison, push mask frame |
| else | 6 | parent mask minus true mask |
| endif | 7 | restore parent mask |
| ballot | 8 | each active lane receives 32-bit predicate ballot |
| reduce_add | 9 | each active lane receives modulo-2^32 sum |

Inputs are driven one instruction per clock with `valid_i`. `ready_o` is hardwired 1. `fault_o`/`commit_o` reject malformed control instructions. Debug ports are nonarchitectural verification hooks. The register file is 16 x 32 x 32 bits (16 Ki-bit) of *behavioral* state; actual SRAM mapping, ports, power, and timing are unverified.

## Status

Local Python/new-model/C++ agreement: **224/224**, 4,945 instructions, 28 surprise cases. RTL execution: **requires Icarus CI**; do not mark PASS until workflow logs confirm. Neither the 2.56 GHz nor 575 W nor 750 mm² targets have been validated.
