# Separate prospective V296 cap-margin experiment; see CAP_MARGIN_REPAIR_PREREG_20261023.md.
# Equal repair protocol for original, optimized, and V296. No adaptive per-variant decisions.
foreach k {V296_LIB V296_TECH_LEF V296_CELL_LEF V296_TRACKS V296_NETLIST V296_TOP V296_RC_SCALE V296_OUT} {
  if {![info exists env($k)]} { error "Missing environment variable $k" }
}
read_lef $env(V296_TECH_LEF)
read_lef $env(V296_CELL_LEF)
read_liberty $env(V296_LIB)
read_verilog $env(V296_NETLIST)
link_design $env(V296_TOP)
initialize_floorplan -die_area {0 0 140 140} -core_area {10 10 130 130} -site FreePDK45_38x28_10R_NP_162NW_34O
source $env(V296_TRACKS)
place_pins -hor_layers metal5 -ver_layers metal6
create_clock -name coreclk -period 3.5 [get_ports clk]
puts "V296_CLOCK_PERIOD_NS 3.5"
puts "V296_CAP_MARGIN_PERCENT 20"
puts "V296_SLEW_MARGIN_PERCENT 10"
set_input_delay -clock coreclk 0.15 [all_inputs -no_clocks]
set_output_delay -clock coreclk 0.15 [all_outputs]
set_input_transition 0.04 [all_inputs -no_clocks]
set_load 0.005 [all_outputs]
set_max_transition 0.25 [current_design]
set_false_path -from [get_ports rst_n]
if {![check_setup]} { error "Unconstrained timing setup" }
set rc $env(V296_RC_SCALE)
set_layer_rc -layer metal3 -resistance [expr {3.57147e-03 * $rc}] -capacitance [expr {1.03981e-01 * $rc}]
set_layer_rc -layer metal5 -resistance [expr {1.50000e-03 * $rc}] -capacitance [expr {1.09256e-01 * $rc}]
set_wire_rc -signal -layer metal3
set_wire_rc -clock -layer metal5
proc v296_repair_metrics {stage} {
  puts "V296_STAGE_BEGIN $stage"
  puts "V296_METRIC stage=$stage area_um2=[expr {[rsz::design_area] * 1.0e12}] slew=[sta::max_slew_violation_count] cap=[sta::max_capacitance_violation_count]"
  report_worst_slack -max -digits 6
  report_design_area
  puts "V296_STAGE_END $stage"
}
global_placement -density 0.45
detailed_placement
estimate_parasitics -placement
v296_repair_metrics placed
# First matched 20/10 percent margin repair, for all designs and both RCs.
repair_design -cap_margin 20 -slew_margin 10
repair_tie_fanout -separation 0 LOGIC0_X1/Z
repair_tie_fanout -separation 0 LOGIC1_X1/Z
repair_timing -setup
detailed_placement
estimate_parasitics -placement
v296_repair_metrics repaired_first
set_routing_layers -signal metal2-metal10
global_route -guide_file "$env(V296_OUT).first.guide" -congestion_iterations 30
estimate_parasitics -global_routing
v296_repair_metrics routed_first
puts "V296_FIRST_CAP_VIOLATORS_BEGIN"
report_check_types -max_capacitance -violators -format end -digits 6
puts "V296_FIRST_CAP_VIOLATORS_END"
write_def "$env(V296_OUT).first.def"
# Second round ALWAYS runs on every variant and RC, not only violators.
estimate_parasitics -placement
repair_design -cap_margin 20 -slew_margin 10
detailed_placement
estimate_parasitics -placement
v296_repair_metrics repaired_second
global_route -guide_file "$env(V296_OUT).final.guide" -congestion_iterations 30
estimate_parasitics -global_routing
v296_repair_metrics routed_final
puts "V296_FINAL_CAP_VIOLATORS_BEGIN"
report_check_types -max_capacitance -violators -format end -digits 6
puts "V296_FINAL_CAP_VIOLATORS_END"
report_checks -path_delay max -fields {slew capacitance fanout} -digits 4
write_def "$env(V296_OUT).final.def"
puts "V296_MARGIN_PHYSICAL_DONE"
