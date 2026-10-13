#!/usr/bin/env bash
set -euo pipefail
python3 research/v142/verification/broadcast_contract.py
mkdir -p build/v142
iverilog -g2012 -s tb_wave32_broadcast_capture -o build/v142/tb  research/v142/rtl/wave32_broadcast_capture.sv research/v142/verification/tb_wave32_broadcast_capture.sv
vvp build/v142/tb | tee build/v142/simulation.log
yosys -Q -p 'read_verilog -sv research/v142/rtl/wave32_broadcast_capture.sv; synth -top vektor_wave32_broadcast_capture; stat' | tee build/v142/synth.log
