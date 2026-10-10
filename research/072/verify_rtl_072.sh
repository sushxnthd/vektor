#!/bin/sh
set -eu
iverilog -g2012 -s tb_replay_fence_072 -o /tmp/tb072 research/071/rtl/bounded_fabric_071.sv research/072/rtl/replay_source_072.sv research/072/rtl/tb_replay_fence_072.sv
vvp /tmp/tb072
