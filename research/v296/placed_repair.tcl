# V296 matched 3.5 ns placed-and-repaired physical discriminator (not signoff).
# Preregistered clock/RC boundary: research/v296/ROUTED_RC_BOUNDARY_AND_3P5NS_PREREG_20261023.md
# Nangate45 only; same die/core, pin layers, timing, utilization and RC model.
# Each variant/scenario is placed from scratch to avoid cross-case contamination.
foreach k {V296_LIB V296_TECH_LEF V296_CELL_LEF V296_TRACKS V296_NETLIST V296_TOP V296_VARIANT V296_RC_SCALE V296_OUT} {
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
set_input_delay -clock coreclk 0.15 [all_inputs -no_clocks]
set_output_delay -clock coreclk 0.15 [all_outputs]
set_input_transition 0.04 [all_inputs -no_clocks]
set_load 0.005 [all_outputs]
set_max_transition 0.25 [current_design]
# Preserve reset timing separately. Only the issue-data discriminator excludes it.
puts "V296_RESET_PATH_REPORT_BEGIN"
report_worst_slack -max -digits 6
puts "V296_RESET_PATH_REPORT_END"
set_false_path -from [get_ports rst_n]
if {![check_setup]} { error "Unconstrained timing setup" }
set rc $env(V296_RC_SCALE)
# OpenROAD-flow-scripts Nangate45 nominal metal3 RC, scaled together.
# These are routing-layer estimates, not extracted routed interconnect.
set_layer_rc -layer metal3 -resistance [expr {3.57147e-03 * $rc}] -capacitance [expr {1.03981e-01 * $rc}]
set_layer_rc -layer metal5 -resistance [expr {1.50000e-03 * $rc}] -capacitance [expr {1.09256e-01 * $rc}]
set_wire_rc -signal -layer metal3
set_wire_rc -clock -layer metal5
proc v296_metrics {stage} {
  puts "V296_STAGE_BEGIN $stage"
  puts "V296_METRIC stage=$stage area_um2=[expr {[rsz::design_area] * 1.0e12}] slew=[sta::max_slew_violation_count] cap=[sta::max_capacitance_violation_count]"
  report_worst_slack -max -digits 6
  report_design_area
  puts "V296_STAGE_END $stage"
}
global_placement -density 0.45
detailed_placement
estimate_parasitics -placement
v296_metrics placed
# Same repair strategy and clock for both controls and V296.
repair_design
repair_tie_fanout -separation 0 LOGIC0_X1/Z
repair_tie_fanout -separation 0 LOGIC1_X1/Z
repair_timing -setup
detailed_placement
estimate_parasitics -placement
v296_metrics repaired
report_checks -path_delay max -fields {slew capacitance fanout} -digits 4
write_def "$env(V296_OUT).repaired.def"
# Routed-wire estimates are stronger than uniform lumped net loads.
# If residual routed electrical violations exist, use exactly one matched
# repair-and-reroute pass; record the preclosure and postclosure evidence.
set_routing_layers -signal metal2-metal10
if {[catch {global_route -guide_file "$env(V296_OUT).guide" -congestion_iterations 30} err]} {
  puts "V296_ROUTE_FAILED $err"
  puts "V296_PHYSICAL_INCOMPLETE"
} else {
  estimate_parasitics -global_routing
  v296_metrics routed_preclosure
  set residual [expr {[sta::max_slew_violation_count] + [sta::max_capacitance_violation_count]}]
  if {$residual > 0} {
    puts "V296_ROUTED_ELECTRICAL_CLOSURE_ATTEMPT residual=$residual"
    if {[catch {
      repair_design
      detailed_placement
      estimate_parasitics -placement
      global_route -guide_file "$env(V296_OUT).guide" -congestion_iterations 30
      estimate_parasitics -global_routing
    } err]} {
      puts "V296_ROUTE_FAILED closure=$err"
      puts "V296_PHYSICAL_INCOMPLETE"
      exit 5
    }
  }
  v296_metrics routed
  report_checks -path_delay max -fields {slew capacitance fanout} -digits 4
  write_def "$env(V296_OUT).routed.def"
  puts "V296_PHYSICAL_DONE"
}
