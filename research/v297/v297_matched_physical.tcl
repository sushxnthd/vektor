# V297 preregistered matched OpenROAD physical kill.
# All three implementations share the same registered shell, physical
# constraints, Nangate45 libraries, routing layers, RC and repair passes.
foreach k {V297_LIB V297_TECH_LEF V297_CELL_LEF V297_TRACKS V297_RCX_RULES V297_NETLIST} {
  if {![info exists env($k)]} {error "MISSING_INPUT $k"}
  if {![file isfile $env($k)]} {error "MISSING_FILE $k"}
}
if {![info exists env(V297_OUT)] || $env(V297_OUT) eq ""} {error "MISSING_OUTPUT_PREFIX"}
read_lef $env(V297_TECH_LEF)
read_lef $env(V297_CELL_LEF)
read_liberty $env(V297_LIB)
read_verilog $env(V297_NETLIST)
link_design v297_matched_shell
initialize_floorplan -die_area {0 0 80 80} -core_area {10 10 70 70} -site FreePDK45_38x28_10R_NP_162NW_34O
source $env(V297_TRACKS)
place_pins -hor_layers metal5 -ver_layers metal6
create_clock -name coreclk -period 3.5 [get_ports clk]
set_input_delay -clock coreclk 0.15 [all_inputs -no_clocks]
set_output_delay -clock coreclk 0.15 [all_outputs]
set_input_transition 0.04 [all_inputs -no_clocks]
set_load 0.005 [all_outputs]
set_clock_uncertainty -setup 0.10 [get_clocks coreclk]
set_clock_uncertainty -hold 0.05 [get_clocks coreclk]
set_max_transition 0.25 [current_design]
set_false_path -from [get_ports rst_n]
if {![check_setup]} {error "V297_UNCONSTRAINED"}
set_layer_rc -layer metal3 -resistance [expr {3.57147e-03 * 2.0}] -capacitance [expr {1.03981e-01 * 2.0}]
set_layer_rc -layer metal5 -resistance [expr {1.50000e-03 * 2.0}] -capacitance [expr {1.09256e-01 * 2.0}]
set_wire_rc -signal -layer metal3
set_wire_rc -clock -layer metal5
puts "V297_FROZEN_CLOCK_NS 3.5"
puts "V297_FROZEN_RC_MULTIPLIER 2.0"
puts "V297_FROZEN_DENSITY 0.45"
global_placement -density 0.45
detailed_placement
estimate_parasitics -placement
puts "V297_PLACED_AREA_UM2 [expr {[rsz::design_area] * 1.0e12}]"
repair_design -cap_margin 20 -slew_margin 10
repair_tie_fanout -separation 0 LOGIC0_X1/Z
repair_tie_fanout -separation 0 LOGIC1_X1/Z
repair_timing -setup
detailed_placement
estimate_parasitics -placement
puts "V297_PRECTS_AREA_UM2 [expr {[rsz::design_area] * 1.0e12}]"
clock_tree_synthesis -buf_list {CLKBUF_X1 CLKBUF_X2 CLKBUF_X3} -root_buf CLKBUF_X3 -wire_unit 20
set_propagated_clock [all_clocks]
estimate_parasitics -placement
repair_design -cap_margin 20 -slew_margin 10
repair_timing -setup
repair_timing -hold
detailed_placement
estimate_parasitics -placement
puts "V297_POSTCTS_AREA_UM2 [expr {[rsz::design_area] * 1.0e12}]"
write_def "$env(V297_OUT).postcts.def"
set_routing_layers -signal metal2-metal10
global_route -guide_file "$env(V297_OUT).guide" -congestion_iterations 30
estimate_parasitics -global_routing
puts "V297_GLOBAL_ROUTE_DONE"
puts "V297_GLOBAL_MAX_SLACK_BEGIN"
report_worst_slack -max -digits 6
puts "V297_GLOBAL_MAX_SLACK_END"
detailed_route -output_drc "$env(V297_OUT).drc.rpt" -output_maze "$env(V297_OUT).maze.log"
puts "V297_DRC_COUNT [detailed_route_num_drvs]"
puts "V297_IS_ROUTED [expr {[design_is_routed] ? 1 : 0}]"
if {![design_is_routed]} {error "V297_NOT_ROUTED"}
define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file $env(V297_RCX_RULES)
adjust_rc -res_factor 2.0 -cc_factor 2.0 -gndc_factor 2.0
write_spef "$env(V297_OUT).spef"
read_spef "$env(V297_OUT).spef"
puts "V297_EXTRACTED_AREA_UM2 [expr {[rsz::design_area] * 1.0e12}]"
puts "V297_EXTRACTED_MAX_SLACK_BEGIN"
report_worst_slack -max -digits 6
puts "V297_EXTRACTED_MAX_SLACK_END"
puts "V297_EXTRACTED_MIN_SLACK_BEGIN"
report_worst_slack -min -digits 6
puts "V297_EXTRACTED_MIN_SLACK_END"
puts "V297_EXTRACTED_CAP_COUNT [sta::max_capacitance_violation_count]"
puts "V297_EXTRACTED_SLEW_COUNT [sta::max_slew_violation_count]"
report_check_types -max_capacitance -violators -format end -digits 6
report_check_types -max_slew -violators -format end -digits 6
write_def "$env(V297_OUT).final.def"
puts "V297_EXTRACTED_DONE"
