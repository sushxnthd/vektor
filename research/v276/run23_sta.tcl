set cfg $::env(CFG)
read_liberty research/v276/run23_ci/nangate45.lib
read_verilog research/v276/run23_ci/${cfg}_mapped.v
link_design v276_warp_rf_map
create_clock -name core -period 1.0 [get_ports clk]
set data_inputs [remove_from_collection [all_inputs] [get_ports clk]]
set_input_delay 0.05 -clock core $data_inputs
set_output_delay 0.05 -clock core [all_outputs]
foreach {transition load} {0.01 0.002 0.05 0.005 0.10 0.010} {
 set_input_transition $transition $data_inputs
 set_load $load [all_outputs]
 puts "V276 CONFIG=$cfg TRANSITION=$transition LOAD=$load"
 report_checks -path_delay max -group_path_count 3
 report_check_types -max_capacitance -max_slew -violators
}
report_design_area
