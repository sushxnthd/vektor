# OpenSTA constraints for V270 mapped-netlist checks. NOT executed in run14.
# Nangate45 Liberty: time 1ns; capacitance 1ff (NOT pF).
# Set MODE, TRAN (ns), CAP (fF), mapped file path in the caller.
read_liberty build/v270/NangateOpenCellLibrary_typical.lib
read_verilog build/v270/mode$::env(MODE)_mapped.v
link_design v270_pack
set_input_transition $::env(TRAN) [all_inputs]
set_load $::env(CAP) [all_outputs]
set_max_delay 4.0 -from [all_inputs] -to [all_outputs]
report_checks -path_delay max -group_path_count 5 -fields {slew cap fanout}
report_check_types -max_capacitance -max_slew -violators
report_worst_slack -max
