# V144 RTL synthesis and simulation evidence — 2026-10-13

**Evidence class:** GitHub Actions Icarus RTL simulation + generic Yosys synthesis, NOT physical area/timing.

Workflow: https://github.com/sushxnthd/vektor/actions/runs/38388858047 (successful, commit 17b7213b62c0be4fb104ed8b04bfc270f24b57e0). The first CI run used a directed two-case smoke test; a subsequent commit upgrades the testbench to 1200 full-Wave32 vectors. The 1200-vector pass must be confirmed by a later CI run before claiming it.

| RTL topology | Generic Yosys cells | Combinational logic depth |
|---|---:|---:|
| One tagged Wave32 response | 81 | 7 |
| Two tagged Wave32 responses, bank conflict filter | 6,238 | 8 |
| Three-input response coalescer | 9,286 | 12 |

**Important comparison caveat:** the three blocks have DIFFERENT response interfaces, gating, and bank policies. Counts are not normalized for equal throughput or full system resources. The two-response router has 33% fewer generic cells than the three-input coalescer but ~77x the single tagged response network. No mapped area, clock period, power, routing or silicon evidence.

**Architectural interpretation:** doubling response bandwidth is potentially valuable in the synthetic short-latency regimes, but the large 1024-bit payload multiplexing cost makes it a physical-feasibility research target, not an automatic upgrade. Next implement per-bank fixed routing or a small operand cache to reduce wide mux cost under equal response capacity.
