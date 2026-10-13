#!/usr/bin/env bash
set -euo pipefail
mkdir -p build/v150
python3 research/v150/verification/gen_vectors.py | tee build/v150/oracle.log
sha256sum build/v150/full_vectors.txt | tee build/v150/oracle_sha256.txt
iverilog -g2012 -s tb_full_reference -o build/v150/tb_full_reference research/v150/rtl/fp32_full_reference.sv research/v150/verification/tb_full_reference.sv
vvp build/v150/tb_full_reference | tee build/v150/tb_full_reference.log
# Elaboration only. 555-bit reference is not a GPU PPA candidate.
timeout 180s yosys -Q -p 'read_verilog -sv research/v150/rtl/fp32_full_reference.sv; hierarchy -top vektor_fp32_full_reference; proc; opt; check -assert; stat' > build/v150/elaborate.log 2>&1
tail -n 24 build/v150/elaborate.log
echo 'V150 reference RTL functional gate PASS; PPA unqualified'
