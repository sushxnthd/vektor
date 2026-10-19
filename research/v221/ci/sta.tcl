read_liberty build/v221/NangateOpenCellLibrary_typical.lib
read_verilog build/v221/$::env(TOP)_mapped.v
link_design $::env(TOP)
create_clock -name vclk -period 1.000
set_input_delay 0.050 -clock vclk [all_inputs]
set_output_delay 0.050 -clock vclk [all_outputs]
set_input_transition $::env(SLEW) [all_inputs]
set_load $::env(LOAD) [all_outputs]
report_checks -path_delay max -group_path_count 3
report_worst_slack -max
report_check_types -max_slew -max_capacitance -violators
