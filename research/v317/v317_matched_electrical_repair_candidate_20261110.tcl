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
# Preserve pre-repair electrical violation lists for a matched delta audit.
foreach {kind option} {max_capacitance -max_capacitance max_slew -max_slew max_fanout -max_fanout} {
  report_check_types $option -violators > [file join $rpt "${label}_pre_${kind}_violators.txt"]
}
repair_design
# Re-estimate from the modified placement. The pre-repair global-route RC
# is stale once repair_design inserts or resizes cells.
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
# Electrical legality is a separate gate from setup/hold slack. Persist the
# actual violating paths, not merely a worst-slack or area summary. These
# reports are placement-RC diagnostics; rerun on extracted detailed route.
foreach phase {pre post} {
  # Pre-repair checks must be captured before repair, so only post is
  # generated here. The pre reports are emitted above before any mutation.
  if {$phase eq "post"} {
    foreach {kind option} {max_capacitance -max_capacitance max_slew -max_slew max_fanout -max_fanout} {
      report_check_types $option -violators > [file join $rpt "${label}_${phase}_${kind}_violators.txt"]
    }
  }
}
write_db $::env(OUTPUT_ODB)
puts "REPAIR_CANDIDATE_ONLY: $label; detailed route, extracted electrical checks, DRC and matched throughput still required"
