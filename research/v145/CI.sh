#!/usr/bin/env bash
set -euo pipefail
mkdir -p build/v145
c++ -std=c++17 -O2 -Wall -Wextra research/v145/verification/selector_check.cpp -o build/v145/selector
build/v145/selector | tee build/v145/selector.log
iverilog -g2012 -s tb_wave32_rf_parity_fixed -o build/v145/router_tb \
 research/v144/rtl/wave32_rf_dual_response.sv \
 research/v145/rtl/wave32_rf_parity_fixed.sv \
 research/v145/verification/tb_wave32_rf_parity_fixed.sv
vvp build/v145/router_tb | tee build/v145/rtl.log
yosys -Q -p 'read_verilog -sv research/v144/rtl/wave32_rf_dual_response.sv; synth -top vektor_wave32_rf_dual_response; stat; ltp -noff' | tee build/v145/synth_flexible.log
yosys -Q -p 'read_verilog -sv research/v145/rtl/wave32_rf_parity_fixed.sv; synth -top vektor_wave32_rf_parity_fixed; stat; ltp -noff' | tee build/v145/synth_fixed.log
python3 research/v145/verification/parse_synth.py
sha256sum research/v145/rtl/*.sv research/v145/verification/* research/v145/CI.sh > build/v145/SHA256SUMS.txt
