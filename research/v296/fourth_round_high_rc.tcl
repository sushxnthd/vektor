# V296 prospective high-RC fourth-round experiment. Frozen protocol:
# research/v296/FOURTH_ROUND_HIGH_RC_PREREG_20261024.md
# This file DOES NOT change the original six-case detailed-route experiment.
foreach k {V296_RCX_RULES V296_DETAIL_RC_MULTIPLIER} {
  if {![info exists env($k)]} { error "Missing environment variable $k" }
}
if {![file isfile $env(V296_RCX_RULES)]} { error "Missing pinned OpenRCX rules" }
if {$env(V296_RC_SCALE) != 2.0 || $env(V296_DETAIL_RC_MULTIPLIER) != 2.0} {
  error "Fourth-round experiment is frozen to high RC only"
}
source research/v296/cap_margin_third.tcl
puts "V296_FOURTH_BEGIN"
puts "V296_FOURTH_SLEW_MARGIN_PERCENT 25"
estimate_parasitics -placement
repair_design -cap_margin 20 -slew_margin 25
repair_timing -setup
detailed_placement
estimate_parasitics -placement
v296_repair_metrics repaired_fourth
global_route -guide_file "$env(V296_OUT).fourth.guide" -congestion_iterations 30
estimate_parasitics -global_routing
v296_repair_metrics routed_fourth
puts "V296_FOURTH_DETAIL_BEGIN"
detailed_route -output_drc "$env(V296_OUT).fourth.drc.rpt" -output_maze "$env(V296_OUT).fourth.maze.log"
set drc [detailed_route_num_drvs]
set routed [design_is_routed]
puts "V296_FOURTH_DRC_COUNT $drc"
puts "V296_FOURTH_IS_ROUTED [expr {$routed ? 1 : 0}]"
if {!$routed} { error "Unrouted nets after detailed route" }
define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file $env(V296_RCX_RULES)
adjust_rc -res_factor 2.0 -cc_factor 2.0 -gndc_factor 2.0
puts "V296_FOURTH_DETAIL_RC_MULTIPLIER 2.0"
write_spef "$env(V296_OUT).fourth.spef"
read_spef "$env(V296_OUT).fourth.spef"
puts "V296_FOURTH_HOLD_BEGIN"
report_worst_slack -min -digits 6
puts "V296_FOURTH_HOLD_END"
v296_repair_metrics extracted_fourth
puts "V296_FOURTH_SLEW_VIOLATORS_BEGIN"
report_check_types -max_slew -violators -format end -digits 6
puts "V296_FOURTH_SLEW_VIOLATORS_END"
puts "V296_FOURTH_CAP_VIOLATORS_BEGIN"
report_check_types -max_capacitance -violators -format end -digits 6
puts "V296_FOURTH_CAP_VIOLATORS_END"
write_def "$env(V296_OUT).fourth.def"
puts "V296_FOURTH_DONE"
