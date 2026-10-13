#!/usr/bin/env bash
set -euo pipefail
mkdir -p build/v149
python3 research/v149/verification/gen_vectors.py | tee build/v149/oracle.log
RTL="research/v144/rtl/wave32_rf_dual_response.sv research/v146/rtl/wave32_operand_collector.sv research/v148/rtl/fp32_mul_lane.sv research/v148/rtl/wave32_mul_slice.sv research/v148/rtl/wave32_mul_frontend.sv research/v149/rtl/fp32_fma_close_accum.sv research/v149/rtl/fp32_close_round.sv research/v149/rtl/wave32_close_slice.sv research/v149/rtl/wave32_close_frontend.sv"
for tb in tb_close_round tb_close_frontend; do
 iverilog -g2012 -s "$tb" -o "build/v149/$tb" $RTL "research/v149/verification/$tb.sv"
 vvp "build/v149/$tb" | tee "build/v149/$tb.log"
done
timeout 240s yosys -Q -p "read_verilog -sv research/v149/rtl/fp32_fma_close_accum.sv research/v149/rtl/fp32_close_round.sv; synth -top vektor_fp32_close_round; stat" > build/v149/synth_close_round.log 2>&1
tail -n 24 build/v149/synth_close_round.log
echo 'V149 bounded RNE close integration and generic synthesis PASS'
