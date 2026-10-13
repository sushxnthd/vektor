#!/usr/bin/env bash
set -euo pipefail
mkdir -p build/v149
python3 research/v149/verification/gen_vectors.py | tee build/v149/oracle.log
sha256sum build/v149/close_vectors.txt | tee build/v149/oracle_sha256.txt
python3 research/v149/verification/workload_probe.py | tee build/v149/workload_probe.json
python3 - <<'PY'
import json
x=json.load(open('build/v149/workload_probe.json'))['workloads']
assert {k:v['close_eligible'] for k,v in x.items()} == {'vector_positive':0,'vector_signed':2159,'gemm_fragments':1042,'cancellation_control':8192,'divergent_active':2081}
print('V149 workload probe frozen counts PASS')
PY
RTL="research/v144/rtl/wave32_rf_dual_response.sv research/v146/rtl/wave32_operand_collector.sv research/v148/rtl/fp32_mul_lane.sv research/v148/rtl/wave32_mul_slice.sv research/v148/rtl/wave32_mul_frontend.sv research/v149/rtl/fp32_fma_close_accum.sv research/v149/rtl/fp32_close_round.sv research/v149/rtl/wave32_close_slice.sv research/v149/rtl/wave32_close_frontend.sv"
for tb in tb_close_round tb_close_frontend; do
 iverilog -g2012 -s "$tb" -o "build/v149/$tb" $RTL "research/v149/verification/$tb.sv"
 vvp "build/v149/$tb" | tee "build/v149/$tb.log"
done
timeout 240s yosys -Q -p "read_verilog -sv research/v149/rtl/fp32_fma_close_accum.sv research/v149/rtl/fp32_close_round.sv; synth -top vektor_fp32_close_round; stat" > build/v149/synth_close_round.log 2>&1
tail -n 24 build/v149/synth_close_round.log
grep -i 'topological' build/v149/synth_close_round.log | tail -n 4 || true
timeout 240s yosys -Q -p "read_verilog -sv $RTL; hierarchy -top vektor_wave32_close_frontend -chparam LANES 1; synth -top vektor_wave32_close_frontend; stat; ltp -noff" > build/v149/synth_front_lane1.log 2>&1
tail -n 24 build/v149/synth_front_lane1.log
grep -i 'topological' build/v149/synth_front_lane1.log | tail -n 4 || true
echo 'V149 bounded RNE close integration and generic synthesis PASS'
