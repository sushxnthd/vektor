#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build results
python3 tests/run_models_054.py
for D in 0 1; do
  for A in 0 25 50 100; do
    for S in 540054 540055 540056; do
      V="build/d${D}_a${A}_s${S}.vec"
      iverilog -g2012 -s tb_rf_tagged_fanout_054 -Ptb_rf_tagged_fanout_054.DEDUP="$D" \
        -o build/tb rtl/rf_tagged_fanout_054.sv rtl/tb_rf_tagged_fanout_054.sv
      vvp build/tb +VECTORS="$V"
    done
  done
done
for D in 0 1; do
  yosys -Q -T -p "read_verilog -sv rtl/rf_tagged_fanout_054.sv; hierarchy -top rf_tagged_fanout_054 -chparam DEDUP $D; synth -top rf_tagged_fanout_054; stat" > "results/yosys_d${D}.log"
done
