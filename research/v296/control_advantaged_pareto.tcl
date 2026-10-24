# V296 preregistered control-advantaged Pareto test; controls get extra repair.
# Frozen protocol: CONTROL_ADVANTAGED_PARETO_PREREG_20261024.md
foreach k {V296_CONTROL_EXTRA V296_VARIANT V296_RCX_RULES V296_RC_SCALE V296_DETAIL_RC_MULTIPLIER} {
  if {![info exists env($k)]} { error "Missing $k" }
}
if {$env(V296_RC_SCALE) != 2.0 || $env(V296_DETAIL_RC_MULTIPLIER) != 2.0} {
  error "Pareto experiment frozen to high RC (2.0)"
}
if {$env(V296_CONTROL_EXTRA) != 0 && $env(V296_CONTROL_EXTRA) != 1} {
  error "Invalid control repair flag"
}
if {$env(V296_VARIANT) eq "pairwise" && $env(V296_CONTROL_EXTRA) != 0} {
  error "V296 must not receive the control-only fifth repair"
}
if {$env(V296_VARIANT) ne "pairwise" && $env(V296_CONTROL_EXTRA) != 1} {
  error "All controls must receive the fifth repair"
}
if {![file isfile $env(V296_RCX_RULES)]} { error "Missing pinned RCX rules" }
source research/v296/cap_margin_third.tcl
puts "V296_PARETO_VARIANT $env(V296_VARIANT)"
puts "V296_PARETO_EXTRA_REPAIR $env(V296_CONTROL_EXTRA)"
# Identical fourth repair for all architectures, as in the prior successful run.
estimate_parasitics -placement
repair_design -cap_margin 20 -slew_margin 25
repair_timing -setup
detailed_placement
estimate_parasitics -placement
v296_repair_metrics pareto_fourth_repaired
global_route -guide_file "$env(V296_OUT).fourth.guide" -congestion_iterations 30
estimate_parasitics -global_routing
v296_repair_metrics pareto_fourth_routed
puts "V296_PARETO_FOURTH_DONE"
# The control architectures receive an extra, more aggressive repair opportunity.
# This is a deliberately adversarial optimization, not equal effort.
if {$env(V296_CONTROL_EXTRA) == 1} {
  estimate_parasitics -placement
  repair_design -cap_margin 20 -slew_margin 35
  repair_timing -setup
  detailed_placement
  estimate_parasitics -placement
  v296_repair_metrics pareto_control_fifth_repaired
  global_route -guide_file "$env(V296_OUT).fifth.guide" -congestion_iterations 30
  estimate_parasitics -global_routing
  v296_repair_metrics pareto_control_fifth_routed
  puts "V296_PARETO_CONTROL_FIFTH_DONE"
}
puts "V296_PARETO_DETAIL_BEGIN"
detailed_route -output_drc "$env(V296_OUT).pareto.drc.rpt" -output_maze "$env(V296_OUT).pareto.maze.log"
puts "V296_PARETO_DRC_COUNT [detailed_route_num_drvs]"
set routed [design_is_routed]
puts "V296_PARETO_IS_ROUTED [expr {$routed ? 1 : 0}]"
if {!$routed} { error "Incomplete detailed routing" }
define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file $env(V296_RCX_RULES)
adjust_rc -res_factor 2.0 -cc_factor 2.0 -gndc_factor 2.0
puts "V296_PARETO_RC_MULTIPLIER 2.0"
write_spef "$env(V296_OUT).pareto.spef"
read_spef "$env(V296_OUT).pareto.spef"
puts "V296_PARETO_HOLD_BEGIN"
report_worst_slack -min -digits 6
puts "V296_PARETO_HOLD_END"
v296_repair_metrics pareto_extracted
puts "V296_PARETO_SLEW_VIOLATORS_BEGIN"
report_check_types -max_slew -violators -format end -digits 6
puts "V296_PARETO_SLEW_VIOLATORS_END"
puts "V296_PARETO_CAP_VIOLATORS_BEGIN"
report_check_types -max_capacitance -violators -format end -digits 6
puts "V296_PARETO_CAP_VIOLATORS_END"
write_def "$env(V296_OUT).pareto.def"
puts "V296_PARETO_DONE"
