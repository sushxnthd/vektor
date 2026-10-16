#!/usr/bin/env bash
set -euo pipefail
mkdir -p build/v156
{ date -u; uname -a; yosys -V; sta -version; iverilog -V | head -n 2; } > build/v156/tool_versions.txt 2>&1
# Keep V155 matched mapping and independent oracle regression as the invariant.
bash research/v155/CI.sh > build/v156/v155_regression.log 2>&1
tail -n 12 build/v156/v155_regression.log
LIB=build/v155/NangateOpenCellLibrary_typical.lib
test "$(git hash-object "$LIB")" = 90e4afb274cfc6514c587c434c77903d554117d1
for mode in control cutset; do
  if [ "$mode" = control ]; then
    TOP=vektor_wave32_buffered_baseline
    FILES="research/v151/rtl/fp32_bounded_tail.sv research/v155/rtl/buffered_control.sv"
  else
    TOP=vektor_wave32_cutset_pipe
    FILES="research/v153/rtl/fp32_cutset_stages.sv research/v153/rtl/wave32_cutset_pipe.sv"
  fi
  timeout 900s yosys -Q -p "read_verilog -sv $FILES; chparam -set LANES 1 $TOP; hierarchy -check -top $TOP; synth -top $TOP -flatten -noabc; check -assert; dfflibmap -liberty $LIB; abc -liberty $LIB; clean; write_verilog -noattr -noexpr build/v156/${mode}_mapped_raw.v; stat -liberty $LIB" > build/v156/${mode}_synth.log 2>&1
  if [ "$mode" = cutset ]; then
    python3 research/v156/normalize_known_concat_lhs.py build/v156/cutset_mapped_raw.v build/v156/cutset_mapped.v --audit build/v156/cutset_normalization_audit.json
  else
    cp build/v156/control_mapped_raw.v build/v156/control_mapped.v
  fi
  python3 research/v156/netlist_syntax_gate.py "build/v156/${mode}_mapped.v" > "build/v156/${mode}_syntax_gate.json"
  export VEKTOR_NETLIST="build/v156/${mode}_mapped.v"
  export VEKTOR_TOP="$TOP"
  export VEKTOR_LIB="$LIB"
  timeout 300s sta -exit research/v156/timing.tcl > build/v156/${mode}_sta.log 2>&1
  if grep -q '^Error:' build/v156/${mode}_sta.log; then
    tail -n 50 build/v156/${mode}_sta.log
    exit 1
  fi
  grep -q 'Startpoint:' build/v156/${mode}_sta.log
  grep -q 'Endpoint:' build/v156/${mode}_sta.log
done
python3 research/v156/summarize.py build/v156 > build/v156/summary.json
cat build/v156/summary.json
