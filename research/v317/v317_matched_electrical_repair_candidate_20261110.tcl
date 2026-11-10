# V317/V296 matched-route electrical repair experiment (OpenROAD Tcl).
# EXPERIMENTAL: not executed or signoff. Invoke separately for compact and
# pairwise from their respective matched post-global-route ODB checkpoints.
# Requires env: INPUT_ODB, OUTPUT_ODB, REPORT_DIR, DESIGN_LABEL.
# Requires the SAME technology, constraints, placement box, routing layers,
# utilization target, wire RC setup and OpenROAD version for both designs.
# Caller must load LEF/LIB/SDC/RC setup before sourcing this file.
foreach key {INPUT_ODB OUTPUT_ODB REPORT_DIR DESIGN_LABEL} {
  if {![info exists ::env($key)] || $::env($key) eq ""} {
    error "Missing required environment variable $key"
  }
}
if {$::env(DESIGN_LABEL) ni {compact pairwise}} {
  error "DESIGN_LABEL must be compact or pairwise"
}
if {![file exists $::env(INPUT_ODB)]} {
  error "Missing input database $::env(INPUT_ODB)"
}
file mkdir $::env(REPORT_DIR)
read_db $::env(INPUT_ODB)
# Physical repair uses the *same* per-design settings. Do not change clock
# constraints or disable timing checks to manufacture a passing result.
estimate_parasitics -global_routing
set rpt $::env(REPORT_DIR)
set label $::env(DESIGN_LABEL)
set pre [open [file join $rpt "${label}_pre_checks.txt"] w]
puts $pre "DESIGN=$label"
puts $pre "INPUT_ODB=$::env(INPUT_ODB)"
close $pre
report_checks -path_delay max -format full_clock_expanded -fields {slew cap fanout} > [file join $rpt "${label}_pre_setup.txt"]
report_checks -path_delay min -format full_clock_expanded -fields {slew cap fanout} > [file join $rpt "${label}_pre_hold.txt"]
# Repair capacitance/slew/fanout first, then hold; re-evaluate both because
# hold buffers and upsizing may create new electrical/setup violations.
repair_design
estimate_parasitics -placement
repair_timing -setup
repair_timing -hold
estimate_parasitics -placement
# No claims of signoff from placement estimates. This ODB is a repair
# candidate for an independent detailed-route + extracted-RC + DRC run.
report_checks -path_delay max -format full_clock_expanded -fields {slew cap fanout} > [file join $rpt "${label}_post_setup.txt"]
report_checks -path_delay min -format full_clock_expanded -fields {slew cap fanout} > [file join $rpt "${label}_post_hold.txt"]
report_worst_slack -max > [file join $rpt "${label}_post_worst_setup.txt"]
report_worst_slack -min > [file join $rpt "${label}_post_worst_hold.txt"]
report_design_area > [file join $rpt "${label}_post_area.txt"]
write_db $::env(OUTPUT_ODB)
puts "REPAIR_CANDIDATE_ONLY: $label; detailed route, extracted electrical checks, DRC and matched throughput still required"
