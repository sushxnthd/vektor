#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=.
mkdir -p build/v150 build/v151
python3 research/v150/verification/gen_vectors.py | tee build/v151/v150_oracle.log
python3 research/v151/verification/gen_boundary.py | tee build/v151/corpus.log
sha256sum build/v151/full_vectors.txt | tee build/v151/corpus.sha256
iverilog -g2012 -s tb_bounded_tail -o build/v151/tb_bounded_tail \
 research/v151/rtl/fp32_bounded_tail.sv research/v151/verification/tb_bounded_tail.sv
vvp build/v151/tb_bounded_tail | tee build/v151/rtl.log
# Synthesis is a generic gate-level proxy, NOT mapped silicon PPA.
timeout 240s yosys -Q -p 'read_verilog -sv research/v151/rtl/fp32_bounded_tail.sv; hierarchy -top vektor_fp32_bounded_tail; proc; opt; techmap; opt; stat; check -assert' > build/v151/generic_synth.log 2>&1
tail -n 35 build/v151/generic_synth.log
echo 'V151 correctness PASS; PPA/tile gates still open'
