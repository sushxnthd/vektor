#!/usr/bin/env bash
set -euo pipefail
for bits in 1 2 3 4; do
  for ver in 094 099; do
    top="wb_final_consumer_${ver}"
    yosys -Q -p "read_verilog -sv rtl/vtile/${top}.sv; chparam -set TAG_BITS ${bits} ${top}; synth -top ${top}; stat" > "/tmp/v099_${ver}_${bits}.log"
    cells=$(grep 'Number of cells:' "/tmp/v099_${ver}_${bits}.log" | tail -1 | awk '{print $4}')
    if [ -z "$cells" ]; then echo "No cell count for $ver $bits"; exit 1; fi
    echo "V099_GENERIC_CELLS tag_bits=$bits policy=$ver cells=$cells"
  done
done
