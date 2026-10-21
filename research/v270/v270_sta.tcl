# V270 final characterized STA attempt. No placement or extracted interconnect.
# CLI: openroad -exit research/v270/v270_sta.tcl MODE LOAD_PF SLEW_NS
set mode [lindex $argv 0]
set load_pf [lindex $argv 1]
set slew_ns [lindex $argv 2]
read_liberty build/v270/NangateOpenCellLibrary_typical.lib
read_verilog build/v270/mode${mode}_mapped.v
link_design v270_pack
set_input_transition $slew_ns [all_inputs]
set_load $load_pf [all_outputs]
set_max_delay 10.0 -from [all_inputs] -to [all_outputs]
puts "V270 STA mode=$mode load_pf=$load_pf slew_ns=$slew_ns"
report_design_area
report_checks -path_delay max -group_path_count 2 -digits 4
report_worst_slack -max
puts "ELECTRICAL_VIOLATIONS_START"
report_check_types -max_capacitance -max_slew -violators
puts "ELECTRICAL_VIOLATIONS_END"
