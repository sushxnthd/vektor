# First V143 hardware CI evidence — 2026-10-13

Commit db409e058015ae6cb66045231aa22cde4ecfbca3
Workflow run https://github.com/sushxnthd/vektor/actions/runs/38381018667
Status: success, completed 2026-10-13.
Independent abstract request/response checker: PASS 3456 cases.
Icarus Verilog: PASS 800 deterministic full-Wave32 test vectors.
Yosys synth (generic gates only): 3-input coalescer 9286 cells, 6144 muxes, longest path 12 generic cells; passthrough 6 cells, longest path 1.
Logs/artifact: https://github.com/sushxnthd/vektor/actions/runs/38381018667/artifacts/11802519107
This is NOT mapped PPA or integrated GPU execution. The passthrough uses more RF reads and is not an equal-functionality energy/area baseline.
