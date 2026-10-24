# V296 independent output-loading falsification: double external load to 10 fF.
# Identical 10 fF policy for V296 and serial one-hot; 5 fF historical run unchanged.
# Frozen before outcomes in CTS45_SETUP250_FINAL_CONTROL_RESCUE_PREREG_20261024.md.
# The existing pre-CTS physical Tcl is NOT modified. CTS is inserted before detailed routing.
foreach k {V296_CONTROL_EXTRA V296_VARIANT V296_RCX_RULES V296_RC_SCALE V296_DETAIL_RC_MULTIPLIER V296_PLACE_DENSITY} {
  if {![info exists env($k)]} { error "Missing $k" }
}
if {$env(V296_RC_SCALE) ne "2.0" || $env(V296_DETAIL_RC_MULTIPLIER) ne "2.0" || $env(V296_PLACE_DENSITY) ne "0.45"} {
  error "CTS45 frozen high-RC 2x and placement density 0.45"
}
if {$env(V296_VARIANT) eq "pairwise"} {
  if {$env(V296_CONTROL_EXTRA) ne "0"} { error "Candidate cannot get control-only repair" }
} elseif {$env(V296_VARIANT) eq "serial_onehot"} {
  if {$env(V296_CONTROL_EXTRA) ne "1"} { error "Serial control must get extra repair" }
} else { error "Invalid CTS contestant" }
if {![file isfile $env(V296_RCX_RULES)]} { error "Missing RCX model" }
source research/v296/cap_margin_third.tcl
# Load stress is applied after the identical three-round pre-CTS placement.
# The common fourth repair, CTS, post-CTS repair and extraction all see 10 fF.
set_load 0.010 [all_outputs]
puts "V296_CTS45_OUTPUT_LOAD_PF 0.010"
puts "V296_CTS45_OUTPUT_LOAD_STAGE POST_THIRD_PRECTS"
puts "V296_CTS45_VARIANT $env(V296_VARIANT)"
puts "V296_CTS45_EXTRA_REPAIR $env(V296_CONTROL_EXTRA)"
# Frozen fourth pre-CTS round, common to both contestants.
estimate_parasitics -placement
repair_design -cap_margin 20 -slew_margin 25
repair_timing -setup
detailed_placement
estimate_parasitics -placement
v296_repair_metrics cts45_fourth_repaired
global_route -guide_file "$env(V296_OUT).fourth.guide" -congestion_iterations 30
estimate_parasitics -global_routing
v296_repair_metrics cts45_fourth_routed
puts "V296_CTS45_FOURTH_DONE"
# Adversarial fifth pre-CTS repair only for serial control.
if {$env(V296_CONTROL_EXTRA) eq "1"} {
  estimate_parasitics -placement
  repair_design -cap_margin 20 -slew_margin 35
  repair_timing -setup
  detailed_placement
  estimate_parasitics -placement
  v296_repair_metrics cts45_fifth_repaired
  global_route -guide_file "$env(V296_OUT).fifth.guide" -congestion_iterations 30
  estimate_parasitics -global_routing
  v296_repair_metrics cts45_fifth_routed
  puts "V296_CTS45_FIFTH_DONE"
}
# A fresh CTS is constructed BEFORE detailed routing; no post-route graft.
set pre_cts_area [expr {[rsz::design_area] * 1.0e12}]
puts "V296_CTS45_PRECTS_AREA_UM2 $pre_cts_area"
write_def "$env(V296_OUT).prects.def"
puts "V296_CTS45_CTS_BEGIN"
clock_tree_synthesis -buf_list {CLKBUF_X1 CLKBUF_X2 CLKBUF_X3} -root_buf CLKBUF_X3 -wire_unit 20
set_propagated_clock [all_clocks]
puts "V296_CTS45_CLOCKS_PROPAGATED 1"
estimate_parasitics -placement
set post_cts_area [expr {[rsz::design_area] * 1.0e12}]
puts "V296_CTS45_POSTCTS_AREA_UM2 $post_cts_area"
v296_repair_metrics cts45_clock_tree
write_def "$env(V296_OUT).postcts.def"
puts "V296_CTS45_CTS_END"
# Same fixed fanout-16 post-CTS repair for both architectures; prior 40%-margin policy otherwise unchanged.
puts "V296_CTS45_FANOUT_POLICY 16"
set_max_fanout 16 [current_design]
repair_design -cap_margin 20 -slew_margin 40
puts "V296_CTS45_SETUP_MARGIN 0.250"
repair_timing -setup -slack_margin 0.250
repair_timing -hold
detailed_placement
estimate_parasitics -placement
v296_repair_metrics cts45_postcts_repaired
global_route -guide_file "$env(V296_OUT).postcts.guide" -congestion_iterations 30
estimate_parasitics -global_routing
v296_repair_metrics cts45_postcts_global
puts "V296_CTS45_DETAIL_BEGIN"
detailed_route -output_drc "$env(V296_OUT).cts45.drc.rpt" -output_maze "$env(V296_OUT).cts45.maze.log"
puts "V296_CTS45_DRC_COUNT [detailed_route_num_drvs]"
puts "V296_CTS45_IS_ROUTED [expr {[design_is_routed] ? 1 : 0}]"
if {![design_is_routed]} { error "CTS45 incomplete detailed route" }
define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file $env(V296_RCX_RULES)
adjust_rc -res_factor 2.0 -cc_factor 2.0 -gndc_factor 2.0
puts "V296_CTS45_RC_MULTIPLIER 2.0"
write_spef "$env(V296_OUT).cts45.spef"
read_spef "$env(V296_OUT).cts45.spef"
puts "V296_CTS45_HOLD_BEGIN"
report_worst_slack -min -digits 6
puts "V296_CTS45_HOLD_END"
v296_repair_metrics cts45_extracted
puts "V296_CTS45_SLEW_VIOLATORS_BEGIN"
report_check_types -max_slew -violators -format end -digits 6
puts "V296_CTS45_SLEW_VIOLATORS_END"
puts "V296_CTS45_CAP_VIOLATORS_BEGIN"
report_check_types -max_capacitance -violators -format end -digits 6
puts "V296_CTS45_CAP_VIOLATORS_END"
write_def "$env(V296_OUT).cts45.def"
puts "V296_CTS45_DONE"
