# V309 source-controlled, prelayout (zero extracted RC) STA.
# All inputs/outputs constrained symmetrically; no hidden pipeline stages.
set lib $::env(LIB_FILE)
set netlist $::env(NETLIST)
set top $::env(TOP_MODULE)
set slew $::env(INPUT_SLEW_NS)
set load $::env(OUTPUT_LOAD_PF)
read_liberty $lib
read_verilog $netlist
link_design $top
create_clock -name virtual_issue_clock -period 1.0
set_input_delay -clock virtual_issue_clock 0 [all_inputs]
set_output_delay -clock virtual_issue_clock 0 [all_outputs]
set_input_transition $slew [all_inputs]
set_load $load [all_outputs]
report_checks -path_delay max
# OpenSTA 2.0.17 (Ubuntu 22.04) lacks report_check_types and
# -group_path_count; electrical violation reporting requires a later tool.
