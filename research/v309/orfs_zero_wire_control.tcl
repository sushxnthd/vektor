# Post-falsification causal attribution control: SAME mapped netlist, SAME
# Liberty, no physical placement or wire RC. Never replace frozen placed result.
read_liberty $::env(V309_LIBERTY)
read_verilog $::env(V309_NETLIST)
link_design $::env(V309_TOP)
read_sdc $::env(V309_SDC)
puts "V309_SAME_NETLIST_ZERO_WIRE_BEGIN"
report_checks -path_delay max
puts "V309_SAME_NETLIST_ZERO_WIRE_END"
