#!/usr/bin/env bash
set -euo pipefail
mkdir -p build/v148
RTL="research/v144/rtl/wave32_rf_dual_response.sv research/v146/rtl/wave32_operand_collector.sv research/v148/rtl/fp32_mul_lane.sv research/v148/rtl/wave32_mul_slice.sv research/v148/rtl/wave32_mul_frontend.sv"
iverilog -g2012 -s tb_wave32_mul_frontend -o build/v148/test $RTL research/v148/verification/tb_wave32_mul_frontend.sv
vvp build/v148/test | tee build/v148/rtl.log
python3 research/v148/verification/gen_mul_vectors.py
iverilog -g2012 -s tb_mul_oracle -o build/v148/oracle_tb $RTL research/v148/verification/tb_mul_oracle.sv
vvp build/v148/oracle_tb | tee build/v148/oracle.log
for n in 1 4; do
 timeout 240s yosys -Q -p "read_verilog -sv research/v148/rtl/fp32_mul_lane.sv research/v148/rtl/wave32_mul_slice.sv; hierarchy -top vektor_wave32_mul_slice -chparam LANES $n; synth -top vektor_wave32_mul_slice; stat" > "build/v148/synth_lane_${n}.log" 2>&1
 tail -n 24 "build/v148/synth_lane_${n}.log"
done
timeout 240s yosys -Q -p "read_verilog -sv $RTL; hierarchy -top vektor_wave32_mul_frontend -chparam LANES 1; synth -top vektor_wave32_mul_frontend; stat" > build/v148/synth_front_lane_1.log 2>&1
tail -n 24 build/v148/synth_front_lane_1.log
echo 'V148 HDL and generic synthesis PASS'
