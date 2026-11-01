# Pre-route Nangate45 cell-delay analysis, not extracted wire RC.
# sta -exit run_rf_sta.tcl liberty mapped_verilog top output_load_pf
if {[llength $argv] != 4} {
    puts stderr "Usage: run_rf_sta.tcl liberty netlist top output_load_pf"
    exit 2
}
set liberty [lindex $argv 0]
set netlist [lindex $argv 1]
set top [lindex $argv 2]
set output_load [lindex $argv 3]
read_liberty $liberty
read_verilog $netlist
link_design $top
set_input_transition 0.02 [all_inputs]
set_load $output_load [all_outputs]
if {[string match "*rotating" $top]} {
    create_clock -name clk -period 10.0 [get_ports clk]
    set data_inputs [remove_from_collection [all_inputs] [get_ports {clk reset}]]
    set_input_delay 0.0 -clock clk $data_inputs
    set_output_delay 0.0 -clock clk [all_outputs]
    set_false_path -from [get_ports reset]
} else {
    create_clock -name virtual -period 10.0
    set_input_delay 0.0 -clock virtual [all_inputs]
    set_output_delay 0.0 -clock virtual [all_outputs]
}
puts "STA_PATH_BEGIN"
report_checks -to [all_outputs] -path_delay max -group_path_count 1
puts "STA_PATH_END"
puts "STA_CONTEXT_BEGIN"
report_design_area
puts "STA_CONTEXT_END"
