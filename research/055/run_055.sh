#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build results
for D in 0 1; do
  iverilog -g2012 -s tb_rf_masked_fanout_055 -Ptb_rf_masked_fanout_055.DEDUP="$D" -o build/tb rtl/rf_masked_fanout_055.sv rtl/tb_rf_masked_fanout_055.sv
  for MODE in zero ptx synth25 synth50 maskstress; do
    for S in 550055 550056 550057 550058; do
      vvp build/tb +VECTORS="build/${MODE}_s${S}_d${D}.vec"
    done
  done
  yosys -Q -T -p "read_verilog -sv rtl/rf_masked_fanout_055.sv; hierarchy -top rf_masked_fanout_055 -chparam DEDUP $D; synth -top rf_masked_fanout_055; check -assert; stat" > "results/yosys_d${D}.log"
done
