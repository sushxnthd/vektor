#!/usr/bin/env bash
set -euo pipefail

# FP32-CLOSE-GATE-025: reproducible local/free-CI gate for the bounded
# cancellation datapath. This intentionally does not synthesize the 556-bit
# golden oracle; it tests the production candidate independently.
mkdir -p build/rtl
python3 verification/fp32/gen_close_vectors.py

iverilog -g2012 -s tb_fp32_fma_close_accum   -o build/rtl/tb_fp32_fma_close_accum   rtl/vtile/fp32_fma_close_accum.sv   verification/rtl/tb_fp32_fma_close_accum.sv
vvp build/rtl/tb_fp32_fma_close_accum | tee build/rtl/fp32_close_sim.log

timeout 180s yosys -p   'read_verilog -sv rtl/vtile/fp32_fma_close_accum.sv; synth -top vektor_fp32_fma_close_accum; stat'   2>&1 | tee build/rtl/fp32_close_yosys.log

echo "FP32-CLOSE-GATE-025 PASS"
