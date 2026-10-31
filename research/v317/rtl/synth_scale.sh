#!/usr/bin/env bash
set -euo pipefail
mkdir -p build/v317
while read -r lanes data_bits warp_bits reg_bits bank_bits; do
    [[ -z "$lanes" ]] && continue
    tag="${lanes}x${data_bits}"
    yosys -p "read_verilog -sv research/v317/rtl/forwarding_gate.sv; chparam -set LANES ${lanes} -set DATA_BITS ${data_bits} -set WARP_BITS ${warp_bits} -set REG_BITS ${reg_bits} -set BANK_BITS ${bank_bits} vektor_v317_forwarding_gate; synth -top vektor_v317_forwarding_gate; stat; ltp -noff; write_json build/v317/synth_${tag}.json" 2>&1 | tee "build/v317/synth_${tag}.log"
done <<'CASES'
4 8 2 4 2
8 16 3 6 3
32 32 5 8 4
CASES
