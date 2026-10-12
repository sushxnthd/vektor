# Vektor-131 — banked RF collector RTL candidate

Scope: synthesizable scalar operand collector with two single-read-port banks, source alias broadcast, scoreboard gating, registered tagged responses, and reset drain handshake. This is not a Wave32 datapath, not synthesized, and not a 5090-class capability claim.

Evidence is provided in the reproducibility archive pending HDL simulation. The first independent C++ comparison uncovered an unintended head-of-line scheduling difference; the final experiment compares both policies explicitly and retains that negative evidence.

Run `python3 run_experiments.py` (requires g++). To run the HDL testbench when Icarus Verilog is available: `iverilog -g2012 -s tb_kpx_rf_collector -o tb.out kpx_rf_collector.sv tb_kpx_rf_collector.sv && vvp tb.out`.
