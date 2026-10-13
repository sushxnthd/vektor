#!/usr/bin/env bash
set -euo pipefail
mkdir -p build/v150 build/v151 build/v153
export PYTHONPATH=.
python3 research/v150/verification/gen_vectors.py > build/v153/v150_oracle.log
python3 research/v151/verification/gen_boundary.py > build/v153/corpus.log
sha256sum build/v151/full_vectors.txt > build/v153/corpus.sha256
iverilog -g2012 -s tb_cutset_pipe -o build/v153/tb research/v151/rtl/fp32_bounded_tail.sv research/v153/rtl/fp32_cutset_stages.sv research/v153/rtl/wave32_cutset_pipe.sv research/v153/verification/tb_cutset_pipe.sv
vvp build/v153/tb > build/v153/rtl.log
cat build/v153/rtl.log
