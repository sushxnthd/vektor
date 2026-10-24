# Prospective separate experiment: source the unchanged frozen two-round flow,
# then apply one additional matched electrical AND setup repair to all six cases.
# Preregistration: THIRD_ROUND_SYMMETRIC_CLOSURE_PREREG_20261023.md.
source research/v296/cap_margin_repair.tcl
puts "V296_THIRD_ROUND_BEGIN"
estimate_parasitics -placement
repair_design -cap_margin 20 -slew_margin 10
repair_timing -setup
detailed_placement
estimate_parasitics -placement
v296_repair_metrics repaired_third
global_route -guide_file "$env(V296_OUT).third.guide" -congestion_iterations 30
estimate_parasitics -global_routing
v296_repair_metrics routed_third
puts "V296_THIRD_CAP_VIOLATORS_BEGIN"
report_check_types -max_capacitance -violators -format end -digits 6
puts "V296_THIRD_CAP_VIOLATORS_END"
report_checks -path_delay max -fields {slew capacitance fanout} -digits 4
write_def "$env(V296_OUT).third.def"
puts "V296_THIRD_PHYSICAL_DONE"
