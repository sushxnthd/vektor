#!/usr/bin/env bash
set -euo pipefail
mkdir -p research/v276/run23_ci
curl -fLsS --retry 3 https://raw.githubusercontent.com/The-OpenROAD-Project/OpenROAD-flow-scripts/master/flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib -o research/v276/run23_ci/nangate45.lib
for cfg in direct xor adaptive; do
 case "$cfg" in
 direct) params='-chparam ADAPTIVE 0 -chparam FIXED_MODE 0';;
 xor) params='-chparam ADAPTIVE 0 -chparam FIXED_MODE 1';;
 adaptive) params='-chparam ADAPTIVE 1 -chparam FIXED_MODE 0';;
 esac
 yosys -p "read_verilog -sv research/v276/warp_rf_map.sv; hierarchy -top v276_warp_rf_map $params; synth -top v276_warp_rf_map -noabc; dfflibmap -liberty research/v276/run23_ci/nangate45.lib; abc -liberty research/v276/run23_ci/nangate45.lib; clean; stat -liberty research/v276/run23_ci/nangate45.lib; write_verilog -noattr research/v276/run23_ci/${cfg}_mapped.v" > "research/v276/run23_ci/${cfg}_synth.log" 2>&1
done
docker run --rm -v "$PWD:/work" -w /work openroad/orfs:26Q3-684-g437bde90c bash -lc 'for cfg in direct xor adaptive; do CFG=$cfg openroad -exit research/v276/run23_sta.tcl > research/v276/run23_ci/${cfg}_sta.log 2>&1 || exit $?; done'
