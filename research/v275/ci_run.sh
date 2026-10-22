#!/bin/sh
set -eu
iverilog -g2012 -s tb -o /tmp/v275_sim research/v275/tlb_join.sv research/v275/tb_tlb_join.sv
vvp /tmp/v275_sim
yosys -Q -p 'read_verilog -sv research/v275/tlb_join.sv; hierarchy -top v275_tlb_join; proc; opt; techmap; opt; stat' > research/v275/yosys_generic.log
printf 'PASS: V275 generic synthesis completed\n'
