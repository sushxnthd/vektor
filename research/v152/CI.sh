#!/usr/bin/env bash
set -euo pipefail
mkdir -p build/v152
# Preserve and rerun the previous full-range correctness and integration gate.
bash research/v151/CI.sh > build/v152/v151_regression.log 2>&1
iverilog -g2012 -s tb_bounded_tree -o build/v152/tb \
 research/v151/rtl/fp32_bounded_tail.sv research/v152/rtl/fp32_bounded_tree.sv \
 research/v152/verification/tb_bounded_tree.sv
vvp build/v152/tb | tee build/v152/differential.log
for mode in original balanced; do
 if [ "$mode" = original ]; then file=research/v151/rtl/fp32_bounded_tail.sv; top=vektor_fp32_bounded_tail; else file=research/v152/rtl/fp32_bounded_tree.sv; top=vektor_fp32_bounded_tree; fi
 timeout 240s yosys -Q -p "read_verilog -sv $file; hierarchy -top $top; proc; opt; techmap; opt; stat; ltp -noff; check -assert" > "build/v152/$mode.yosys.log" 2>&1
 grep -E 'number of cells|Number of cells|Longest topological path|length=' "build/v152/$mode.yosys.log" | tail -n 8 || true
done
python3 research/v152/verification/lod_independent.py | tee build/v152/lod_independent.log
python3 research/v152/verification/summary.py > build/v152/summary.json
cat build/v152/summary.json
