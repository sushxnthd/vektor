#!/usr/bin/env bash
set -euo pipefail
mkdir -p build/v155 build/v150 build/v151 build/v153
export PYTHONPATH=.
{ date -u; yosys -V; iverilog -V | head -n 2; } > build/v155/tool_versions.txt 2>&1
bash research/v153/CI.sh > build/v155/v153_regression.log 2>&1
tail -n 2 build/v155/v153_regression.log
sed 's/vektor_wave32_cutset_pipe/vektor_wave32_buffered_baseline/g' research/v153/verification/tb_cutset_pipe.sv > build/v155/tb_control.sv
iverilog -g2012 -s tb_cutset_pipe -o build/v155/tb_control research/v151/rtl/fp32_bounded_tail.sv research/v155/rtl/buffered_control.sv build/v155/tb_control.sv
vvp build/v155/tb_control > build/v155/control_rtl.log
grep 'V153 PASS: 24220' build/v155/control_rtl.log
sha256sum build/v151/full_vectors.txt > build/v155/oracle.sha256
LIB=build/v155/NangateOpenCellLibrary_typical.lib
curl -fL --retry 3 --silent --show-error https://raw.githubusercontent.com/The-OpenROAD-Project/OpenROAD-flow-scripts/6b305a712966be72d8908695c04398acdbe273ca/flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib -o "$LIB"
test "$(git hash-object "$LIB")" = 90e4afb274cfc6514c587c434c77903d554117d1
for mode in control cutset; do
 if [ "$mode" = control ]; then
  TOP=vektor_wave32_buffered_baseline
  FILES="research/v151/rtl/fp32_bounded_tail.sv research/v155/rtl/buffered_control.sv"
 else
  TOP=vektor_wave32_cutset_pipe
  FILES="research/v153/rtl/fp32_cutset_stages.sv research/v153/rtl/wave32_cutset_pipe.sv"
 fi
 timeout 900s yosys -Q -p "read_verilog -sv $FILES; chparam -set LANES 1 $TOP; hierarchy -check -top $TOP; synth -top $TOP -flatten -noabc; check -assert; dfflibmap -liberty $LIB; abc -liberty $LIB; clean; stat -liberty $LIB" > build/v155/${mode}_mapped.log 2>&1
done
python3 research/v155/summarize.py build/v155 > build/v155/summary.json
cat build/v155/summary.json
