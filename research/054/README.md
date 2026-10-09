# Vektor-054 — tagged operand collection and alias fanout

Experimental two-slot, three-source tagged operand collector. `DEDUP=0` reads each logical source; `DEDUP=1` reads one copy of each distinct same-instruction physical register. Requests and returns carry instruction identity and operand index. Invalid responses raise sticky error; completion is valid/ready.

## Verified milestone — 2026-10-09

- 24 x 2500-cycle independent Python reference traces and packed-state replication: **60,000 model cycles, 0 disagreements**.
- GitHub Actions Icarus Verilog: **24/24 differential RTL simulations PASS** against Python vectors, including invalid-return detection.
- Equal-budget generic Yosys synthesis: **2139 generic cells DEDUP=0; 2323 DEDUP=1**, +184 (+8.60%) cells; **272 flip-flop cells** in each. Yosys `check` reports 0 problems.
- This is a generic cell-count proxy, **not** silicon area, power, frequency, critical path, or GPU performance.
- The synthetic model completes 0%, 5.77%, 16.35%, and 47.22% more instructions at deliberate 0/25/50/100% alias levels; no realistic source-alias distribution is known.

Evidence: [CI run](https://github.com/sushxnthd/vektor/actions/runs/37880347241), [full logs and generated vectors](https://github.com/sushxnthd/vektor/actions/runs/37880347241/artifacts/11593903950), `RESULTS_054.md`.

## Reproduce

`python3 research/054/tests/run_models_054.py` (Python 3 standard library only). With free Icarus Verilog and Yosys installed, `bash research/054/run_054.sh` runs the Python model, 24 RTL differential tests, and two generic synthesis configurations.

Raw software results: `results/model_runs_054.csv`. Generated vectors are reproducible. This is not a full RF: it has two instruction slots, one read request port, no RF banks, no wave scoreboard, no realistic ISA/compiler traces, and no physical timing.

Prior art: GPGPU-Sim operand collector documentation https://github.com/gpgpu-sim/gpgpu-sim_distribution/wiki/test1 . No architectural novelty claim.

**Next decisive action:** realistic compiler alias traces and finite-bank/multi-slot PPA comparisons. RTX 5090-class gate remains INCONCLUSIVE.
