# Vektor-054 — tagged operand collection and alias fanout

Experimental, two-slot, three-source tagged operand collector. HDL supports DEDUP=0 (three independent source reads) and DEDUP=1 (one request per distinct same-instruction physical register). Requests and returns carry instruction identity and operand index. A malformed return raises sticky resp_error. Completion uses valid/ready. This is **not** a complete V-Tile or physical register file.

## Evidence (2026-10-09)

- **Executed locally:** 24 x 2500-cycle Python transaction-reference traces independently replicated by a separate packed-state model: 60,000 checked cycles; no mismatches. All traces inject an invalid return and detect it. Zero-alias controls exactly match.
- **Prepared, not yet independently confirmed:** synthesizable SystemVerilog, differential vector testbench, and equal-budget Yosys generic synthesis.
- **Unverified:** HDL simulation, synthesis cell counts, timing, power, real compiler register alias frequencies, bank behavior, GPU performance, and architectural novelty.
- GitHub Actions on this branch are intended to perform the missing HDL checks. A passing generic synthesis report is not evidence of achievable 2.56 GHz or <=575 W.

## Reproduce

Run `python3 research/054/tests/run_models_054.py` (Python 3 standard library only).
For RTL and generic synthesis, install open-source Icarus Verilog and Yosys, then `bash research/054/run_054.sh`.
The shell runner generates 24 deterministic vectors, compares every RTL output cycle, and synthesizes DEDUP=0/1 with the same Yosys script. Raw results are in `results/model_runs_054.csv`; all other vectors are regenerable.

## Model outcomes, three 2500-cycle seeds each

| Injected same-instruction alias probability | Baseline completed | Dedup completed | Relative completed change | Baseline reads | Dedup reads |
|---|---:|---:|---:|---:|---:|
| 0% | 936 | 936 | 0% | 2820 | 2820 |
| 25% | 936 | 990 | +5.77% | 2820 | 2486 |
| 50% | 936 | 1089 | +16.35% | 2820 | 2190 |
| 100% | 936 | 1378 | +47.22% | 2820 | 1383 |

Counts are **synthetic software-model** events, not hardware IPC. Total reads compare different completed-instruction counts; normalize reads per completion for a per-instruction traffic comparison. No bank arbitration or multiport RF is modeled. The 100% alias case is a deliberately extreme stress test.

## Prior art

Operand collectors and banked register-file arbitration are established, including GPGPU-Sim: https://github.com/gpgpu-sim/gpgpu-sim_distribution/wiki/test1 . This work does not assert novelty.

## Single next action

Require green differential RTL simulation on all 24 traces and equal-budget generic Yosys synthesis, then expand to finite bank ports and realistic compiler-derived operand alias statistics.
