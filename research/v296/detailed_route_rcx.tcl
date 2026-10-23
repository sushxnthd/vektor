# Frozen protocol: DETAILED_ROUTE_RCX_PREREG_20261023.md.
# No post-route resizing; source the unchanged, preregistered third-round flow.
foreach k {V296_RCX_RULES V296_DETAIL_RC_MULTIPLIER} {
  if {![info exists env($k)]} { error "Missing environment variable $k" }
}
if {![file isfile $env(V296_RCX_RULES)]} { error "Missing pinned OpenRCX rules" }
source research/v296/cap_margin_third.tcl
puts "V296_DETAIL_BEGIN"
detailed_route -output_drc "$env(V296_OUT).detail.drc.rpt" -output_maze "$env(V296_OUT).detail.maze.log"
set n_drc [detailed_route_num_drvs]
set routed [design_is_routed]
puts "V296_DETAIL_DRC_COUNT $n_drc"
puts "V296_DETAIL_IS_ROUTED [expr {$routed ? 1 : 0}]"
if {!$routed} { error "Unrouted nets after detailed route" }
# Revision-pinned Nangate45 research calibration, not a foundry signoff deck.
extract_parasitics -ext_model_file $env(V296_RCX_RULES)
set factor $env(V296_DETAIL_RC_MULTIPLIER)
if {$factor != 1.0} {
  adjust_rc -res_factor $factor -cc_factor $factor -gndc_factor $factor
}
puts "V296_DETAIL_RC_MULTIPLIER $factor"
write_spef "$env(V296_OUT).detail.spef"
read_spef "$env(V296_OUT).detail.spef"
puts "V296_EXTRACTED_MIN_SLACK_BEGIN"
report_worst_slack -min -digits 6
puts "V296_EXTRACTED_MIN_SLACK_END"
v296_repair_metrics extracted_detail
report_checks -path_delay max -fields {slew capacitance fanout} -digits 4
report_checks -path_delay min -fields {slew capacitance fanout} -digits 4
write_def "$env(V296_OUT).detail.def"
puts "V296_DETAILED_PHYSICAL_DONE"
