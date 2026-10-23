# V296 matched mapped-netlist STA, NOT placed/extracted timing.
# Inputs are supplied via environment variables by run_sta.sh.
foreach key {V296_LIB V296_NETLIST V296_TOP V296_WIRE_CAP V296_WIRE_R V296_VARIANT} {
  if {![info exists env($key)]} { error "Missing $key" }
}
read_liberty $env(V296_LIB)
read_verilog $env(V296_NETLIST)
link_design $env(V296_TOP)
create_clock -name coreclk -period 2.0 [get_ports clk]
set_input_delay -clock coreclk 0.15 [all_inputs -no_clocks]
set_output_delay -clock coreclk 0.15 [all_outputs]
set_input_transition 0.04 [all_inputs -no_clocks]
set_load 0.005 [all_outputs]
# Equal per-net lumped RC sensitivity proxy. NOT extracted physical interconnect.
set_load $env(V296_WIRE_CAP) [get_nets *]
set_resistance $env(V296_WIRE_R) [get_nets *]
set_max_transition 0.25 [current_design]
puts "V296_CASE variant=$env(V296_VARIANT) cap_pf=$env(V296_WIRE_CAP) resistance_kohm=$env(V296_WIRE_R)"
report_units
if {![check_setup]} { error "Unconstrained or malformed STA setup" }
# Record full-design worst slack, including asynchronous reset recovery.
# This is NOT the issue-path performance metric.
puts "V296_ALL_PATH_WORST_SLACK_START"
report_worst_slack -max -digits 6
puts "V296_ALL_PATH_WORST_SLACK_END"
# Reset recovery is a separate correctness constraint. Exclude reset paths only
# from the issue-data critical-path discriminator; retain all-path evidence above.
set_false_path -from [get_ports rst_n]
puts "V296_DATA_WORST_SLACK_START"
report_worst_slack -max -digits 6
puts "V296_DATA_WORST_SLACK_END"
puts "V296_DATA_PATHS_START"
report_checks -path_delay max -group_path_count 3 -fields {slew capacitance fanout} -digits 4
puts "V296_DATA_PATHS_END"
puts "V296_ELECTRICAL_VIOLATORS_START"
report_check_types -max_slew -max_capacitance -violators -max_count 10000
puts "V296_ELECTRICAL_VIOLATORS_END"
puts "V296_STA_COMPLETE"
