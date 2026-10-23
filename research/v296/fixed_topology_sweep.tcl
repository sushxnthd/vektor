# V296 preregistered fixed-topology RC/load sensitivity; nominal placement only.
# No synthesis, resizing, placement or routing after the frozen nominal implementation.
if {![info exists env(V296_RC_SCALE)] || $env(V296_RC_SCALE) ne "1.0"} {
  error "Fixed topology requires nominal RC=1.0"
}
source research/v296/placed_repair.tcl
if {![file exists "$env(V296_OUT).routed.def"]} {
  error "Nominal global route unavailable; fixed-topology test unsupported"
}
puts "V296_FIXED_BEGIN"
write_def "$env(V296_OUT).fixed_reference.def"
foreach {rc_label rc} {05 0.5 10 1.0 20 2.0} {
  set_layer_rc -layer metal3 -resistance [expr {3.57147e-03 * $rc}] -capacitance [expr {1.03981e-01 * $rc}]
  set_layer_rc -layer metal5 -resistance [expr {1.50000e-03 * $rc}] -capacitance [expr {1.09256e-01 * $rc}]
  set_wire_rc -signal -layer metal3
  set_wire_rc -clock -layer metal5
  foreach {load_label load} {025 0.0025 050 0.005 100 0.010} {
    set_load $load [all_outputs]
    estimate_parasitics -global_routing
    set stage [format "fixed_rc%s_load%s" $rc_label $load_label]
    v296_metrics $stage
    write_def "$env(V296_OUT).$stage.def"
  }
}
puts "V296_FIXED_END"

# Prospective interpolation test: numerical forecasts and 40 ps tolerance were
# frozen in FIXED_TOPOLOGY_SENSITIVITY_FALSIFICATION_20261023.md BEFORE these runs.
# This is NOT a workload holdout and cannot overturn the failed electrical gate.
puts "V296_INTERMEDIATE_BEGIN"
set_load 0.005 [all_outputs]
foreach {label rc} {125 1.25 150 1.50 175 1.75} {
  set_layer_rc -layer metal3 -resistance [expr {3.57147e-03 * $rc}] -capacitance [expr {1.03981e-01 * $rc}]
  set_layer_rc -layer metal5 -resistance [expr {1.50000e-03 * $rc}] -capacitance [expr {1.09256e-01 * $rc}]
  set_wire_rc -signal -layer metal3
  set_wire_rc -clock -layer metal5
  estimate_parasitics -global_routing
  set stage "intermediate_rc$label"
  v296_metrics $stage
  write_def "$env(V296_OUT).$stage.def"
}
puts "V296_INTERMEDIATE_END"
