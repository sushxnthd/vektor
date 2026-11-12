# Placement-estimated parasitics only. NOT routed/extracted signoff.
set db $::env(V310_PLACED_DB)
set lib $::env(V310_LIBERTY)
set sdc $::env(V310_SDC)
if {![file exists $db] || ![file exists $lib] || ![file exists $sdc]} {
  error "V310_MISSING_PHYSICAL_INPUT"
}
read_db $db
read_liberty $lib
read_sdc $sdc
set_wire_rc -signal -layer metal3
estimate_parasitics -placement
puts "V310_PLACEMENT_ESTIMATED_RC_BEGIN"
report_checks -path_delay max
puts "V310_PLACEMENT_ELECTRICAL_BEGIN"
report_check_types -max_slew -max_capacitance -violators
puts "V310_PLACEMENT_ELECTRICAL_END"
puts "V310_PLACEMENT_ESTIMATED_RC_END"
