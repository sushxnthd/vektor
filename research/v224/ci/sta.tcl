set lib [lindex $argv 0]
set netlist [lindex $argv 1]
set top [lindex $argv 2]
set load [lindex $argv 3]
read_liberty $lib
read_verilog $netlist
link_design $top
create_clock -name vclk -period 2.0
set_input_delay 0.10 -clock vclk [all_inputs]
set_output_delay 0.10 -clock vclk [all_outputs]
set_load $load [all_outputs]
report_checks -path_delay max -group_path_count 3
report_check_types -max_slew -max_capacitance -violators
report_design_area
