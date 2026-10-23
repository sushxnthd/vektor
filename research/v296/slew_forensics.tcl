# Frozen high-RC V296 post-route slew forensics; see HIGH_RC_SLEW_FORENSICS_PREREG_20261024.md.
# Rehydrate the *existing* routed design and extracted SPEF. NO optimization commands.
foreach k {V296_LIB V296_TECH_LEF V296_CELL_LEF V296_NETLIST V296_DEF V296_SPEF} {
  if {![info exists env($k)] || ![file isfile $env($k)]} {
    error "Missing immutable replay input $k"
  }
}
read_lef $env(V296_TECH_LEF)
read_lef $env(V296_CELL_LEF)
read_liberty $env(V296_LIB)
read_verilog $env(V296_NETLIST)
link_design v296_issue_core
read_def $env(V296_DEF)
create_clock -name coreclk -period 3.5 [get_ports clk]
set_input_delay -clock coreclk 0.15 [all_inputs -no_clocks]
set_output_delay -clock coreclk 0.15 [all_outputs]
set_input_transition 0.04 [all_inputs -no_clocks]
set_load 0.005 [all_outputs]
set_max_transition 0.25 [current_design]
set_false_path -from [get_ports rst_n]
if {![check_setup]} { error "Unconstrained timing setup in replay" }
read_spef $env(V296_SPEF)
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
