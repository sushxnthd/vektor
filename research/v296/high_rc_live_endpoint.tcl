# Single-case live endpoint diagnostic. Do not alter original detailed-route flow.
# Frozen protocol: HIGH_RC_LIVE_ENDPOINT_PREREG_20261024.md.
source research/v296/detailed_route_rcx.tcl
puts "V296_FORENSIC_REPLAY_BEGIN"
puts "V296_FORENSIC_METRIC area_um2=[expr {[rsz::design_area] * 1.0e12}] slew=[sta::max_slew_violation_count] cap=[sta::max_capacitance_violation_count]"
puts "V296_FORENSIC_SETUP_BEGIN"
report_worst_slack -max -digits 6
puts "V296_FORENSIC_SETUP_END"
puts "V296_FORENSIC_HOLD_BEGIN"
report_worst_slack -min -digits 6
puts "V296_FORENSIC_HOLD_END"
puts "V296_FORENSIC_SLEW_VIOLATORS_BEGIN"
report_check_types -max_slew -violators -format end -digits 6
puts "V296_FORENSIC_SLEW_VIOLATORS_END"
puts "V296_FORENSIC_CAP_VIOLATORS_BEGIN"
report_check_types -max_capacitance -violators -format end -digits 6
puts "V296_FORENSIC_CAP_VIOLATORS_END"
puts "V296_FORENSIC_REPLAY_DONE"
