#!/usr/bin/env bash
set -euo pipefail
mkdir -p research/057/build research/057/results
python3 research/057/tests/generate_arb_vectors_057.py
for p in 0 1 2 3; do
  iverilog -g2012 -s tb_rf_return_select_057 -Ptb_rf_return_select_057.POLICY="$p" \
    -o "research/057/build/rtl_p${p}.vvp" \
    research/057/rtl/rf_return_select_057.sv research/057/rtl/tb_rf_return_select_057.sv
  vvp "research/057/build/rtl_p${p}.vvp" "+VECTORS=research/057/build/vectors_p${p}.txt"
  yosys -Q -T -p "read_verilog -sv research/057/rtl/rf_return_select_057.sv; chparam -set POLICY $p rf_return_select_057; hierarchy -top rf_return_select_057; synth -top rf_return_select_057; stat" \
    > "research/057/results/yosys_p${p}_057.log"
done
vvp research/057/build/rtl_p2.vvp +VECTORS=research/057/build/vectors_p3.txt
