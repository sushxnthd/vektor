# Pre-route Nangate45 cell-delay analysis, not extracted wire RC.
# STA_LIBERTY=... STA_NETLIST=... STA_TOP=... STA_LOAD=... sta -exit run_rf_sta.tcl
foreach name {STA_LIBERTY STA_NETLIST STA_TOP STA_LOAD} {
    if {![info exists ::env($name)]} {
        puts stderr "Missing required environment variable $name"
        exit 2
    }
}
set liberty $::env(STA_LIBERTY)
set netlist $::env(STA_NETLIST)
set top $::env(STA_TOP)
set output_load $::env(STA_LOAD)
read_liberty $liberty
read_verilog $netlist
link_design $top
set_input_transition 0.02 [all_inputs]
set_load $output_load [all_outputs]
if {[string match "*rotating" $top]} {
    create_clock -name clk -period 10.0 [get_ports clk]
    set data_inputs [get_ports {request_valid src0_bank_flat src1_bank_flat}]
    set_input_delay 0.0 -clock clk $data_inputs
    set_output_delay 0.0 -clock clk [all_outputs]
    set_false_path -from [get_ports reset]
} else {
    create_clock -name virtual -period 10.0
    set_input_delay 0.0 -clock virtual [all_inputs]
    set_output_delay 0.0 -clock virtual [all_outputs]
}
puts "STA_PATH_BEGIN"
report_checks -to [all_outputs] -path_delay max
puts "STA_PATH_END"

puts "STA_ELECTRICAL_BEGIN"
report_check_types
puts "STA_ELECTRICAL_END"
