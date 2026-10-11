#!/bin/bash
set -euo pipefail
g++ -O2 -std=c++17 -Wall -Wextra -pedantic research/097/replicate_stable.cpp -o /tmp/v97rep
for cfg in '2 2 97' '4 4 1097' '4 16 2097' '4 4 3097'; do
 set -- $cfg
 /tmp/v97rep research/097/vectors_s${1}_g${2}_seed${3}.txt "$1" "$2"
 iverilog -g2012 -s tb_return_stable_097 -Ptb_return_stable_097.SOURCES="$1" -Ptb_return_stable_097.GUARD="$2" -o /tmp/v97extra rtl/vtile/wb_return_stable_arbiter_097.sv research/097/tb_return_stable_097.sv
 vvp /tmp/v97extra +VECTORS=research/097/vectors_s${1}_g${2}_seed${3}.txt
done
