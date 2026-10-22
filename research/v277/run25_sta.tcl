# Unplaced Nangate45 timing/load sensitivity, not signoff
set cfg $::env(CFG)
set top $::env(TOP)
read_liberty research/v277/run25_ci/nangate45.lib
read_verilog research/v277/run25_ci/${cfg}_mapped.v
link_design $top
create_clock -name core -period 1.0 [get_ports clk]
set data_inputs [remove_from_collection [all_inputs] [get_ports clk]]
set_input_delay 0.05 -clock core $data_inputs
set_output_delay 0.05 -clock core [all_outputs]
foreach {transition load} {0.01 0.002 0.05 0.005 0.10 0.010} {
 set_input_transition $transition $data_inputs
 set_load $load [all_outputs]
 puts "RUN25 CONFIG=$cfg INPUT_TRANSITION_NS=$transition OUTPUT_LOAD_PF=$load"
 report_checks -path_delay max -group_path_count 3
 report_check_types -max_capacitance -max_slew -violators
}
report_design_area
