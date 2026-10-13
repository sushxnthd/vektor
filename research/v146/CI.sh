#!/bin/sh
set -eu
mkdir -p build/v146
iverilog -g2012 -s tb_wave32_operand_collector -o build/v146/tb research/v144/rtl/wave32_rf_dual_response.sv research/v146/rtl/wave32_operand_collector.sv research/v146/verification/tb_wave32_operand_collector.sv
vvp build/v146/tb | tee build/v146/rtl.log
yosys -Q -p 'read_verilog -sv research/v144/rtl/wave32_rf_dual_response.sv research/v146/rtl/wave32_operand_collector.sv; synth -top vektor_wave32_operand_collector; stat; ltp -noff' | tee build/v146/synth_collector.log
