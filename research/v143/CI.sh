#!/usr/bin/env bash
set -euo pipefail
mkdir -p build/v143
python3 research/v143/verification/rf_coalescing_oracle.py | tee build/v143/abstract.log
iverilog -g2012 -s tb_wave32_rf_read_coalescer -o build/v143/tb research/v143/rtl/wave32_rf_read_coalescer.sv research/v143/verification/tb_wave32_rf_read_coalescer.sv
vvp build/v143/tb | tee build/v143/rtl_simulation.log
yosys -Q -p 'read_verilog -sv research/v143/rtl/wave32_rf_read_coalescer.sv; synth -top vektor_wave32_rf_read_coalescer; stat; ltp -noff' | tee build/v143/synth_coalesced.log
yosys -Q -p 'read_verilog -sv research/v143/rtl/wave32_rf_read_passthrough.sv; synth -top vektor_wave32_rf_read_passthrough; stat; ltp -noff' | tee build/v143/synth_passthrough.log
iverilog -g2012 -s tb_wave32_rf_single_response -o build/v143/tb_single research/v143/rtl/wave32_rf_single_response.sv research/v143/verification/tb_wave32_rf_single_response.sv
vvp build/v143/tb_single | tee build/v143/rtl_single_response.log
yosys -Q -p 'read_verilog -sv research/v143/rtl/wave32_rf_single_response.sv; synth -top vektor_wave32_rf_single_response; stat; ltp -noff' | tee build/v143/synth_single_response.log
