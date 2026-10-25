# Read-only reconstitution of the original V296 post-route, post-CTS STA.
# No optimization, placement, routing, rescaling or new architecture.
foreach k {V296_ORIGINAL_ROOT V296_TILE_VARIANT V296_LIB V296_TECH_LEF V296_CELL_LEF} {
  if {![info exists env($k)]} { error "Missing $k" }
}
set variant $env(V296_TILE_VARIANT)
if {$variant ne "pairwise" && $variant ne "serial_onehot"} { error "Unknown contestant" }
set root $env(V296_ORIGINAL_ROOT)
set netlist "$root/$variant.v"
set def "$root/$variant.high.cts45.def"
set spef "$root/$variant.high.cts45.spef"
foreach f [list $netlist $def $spef $env(V296_LIB) $env(V296_TECH_LEF) $env(V296_CELL_LEF)] {
  if {![file isfile $f] || [file size $f] == 0} { error "Missing original input $f" }
}
read_lef $env(V296_TECH_LEF)
read_lef $env(V296_CELL_LEF)
read_liberty $env(V296_LIB)
read_verilog $netlist
link_design v296_tile_slice
read_def $def
create_clock -name coreclk -period 3.5 [get_ports clk]
set_input_delay -clock coreclk 0.15 [all_inputs -no_clocks]
set_output_delay -clock coreclk 0.15 [all_outputs]
set_input_transition 0.04 [all_inputs -no_clocks]
set_load 0.005 [all_outputs]
set_max_transition 0.25 [current_design]
set_false_path -from [get_ports rst_n]
set_propagated_clock [all_clocks]
if {![check_setup]} { error "Unconstrained reconstructed design" }
# SPEF contains the original 2x-adjusted RC. NEVER adjust_rc a second time.
read_spef $spef
puts "V296_FORENSIC_START $variant"
puts "V296_FORENSIC_COUNTS area_um2=[expr {[rsz::design_area] * 1.0e12}] slew=[sta::max_slew_violation_count] cap=[sta::max_capacitance_violation_count]"
puts "V296_FORENSIC_SETUP_SLACK_BEGIN"
report_worst_slack -max -digits 6
puts "V296_FORENSIC_SETUP_SLACK_END"
puts "V296_FORENSIC_HOLD_SLACK_BEGIN"
report_worst_slack -min -digits 6
puts "V296_FORENSIC_HOLD_SLACK_END"
puts "V296_FORENSIC_SETUP_PATHS_BEGIN"
report_checks -path_delay max -group_path_count 5 -fields {slew capacitance fanout} -digits 6
puts "V296_FORENSIC_SETUP_PATHS_END"
puts "V296_FORENSIC_HOLD_PATHS_BEGIN"
report_checks -path_delay min -group_path_count 5 -fields {slew capacitance fanout} -digits 6
puts "V296_FORENSIC_HOLD_PATHS_END"
puts "V296_FORENSIC_CAP_VIOLATORS_BEGIN"
report_check_types -max_capacitance -violators -format end -digits 6
puts "V296_FORENSIC_CAP_VIOLATORS_END"
puts "V296_FORENSIC_DONE $variant"
