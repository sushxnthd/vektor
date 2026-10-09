#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build results
for spec in '3 1' '4 2' '8 4' '32 16'; do
  read -r W B <<< "$spec"
  for P in 0 1 2; do
    V="build/w${W}_b${B}_p${P}.vec"
    python3 tests/generate_vectors.py "$W" "$B" "$P" "$V"
    iverilog -g2012 -s tb_rf_policy_052 -Ptb_rf_policy_052.W="$W" -Ptb_rf_policy_052.B="$B" -Ptb_rf_policy_052.POLICY="$P" -o build/sim rtl/rf_policy_052.sv rtl/tb_rf_policy_052.sv
    vvp build/sim +VECTORS="$V"
  done
done
for P in 0 1 2; do
  for spec in '4 2' '8 4'; do
    read -r W B <<< "$spec"
    yosys -Q -T -p "read_verilog -sv rtl/rf_policy_052.sv; hierarchy -top rf_policy_052 -chparam W $W -chparam B $B -chparam POLICY $P; synth -top rf_policy_052; stat" > "results/yosys_w${W}_b${B}_p${P}.log"
  done
done
