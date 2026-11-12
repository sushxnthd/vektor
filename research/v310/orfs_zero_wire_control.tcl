# Prospective same-netlist causal attribution control: SAME mapped netlist, SAME
# Liberty, no physical placement or wire RC. Keep identical netlist and toolchain for zero-wire comparison.
read_lef "$::env(V310_PLATFORM_DIR)/lef/NangateOpenCellLibrary.tech.lef"
read_lef "$::env(V310_PLATFORM_DIR)/lef/NangateOpenCellLibrary.macro.mod.lef"
read_liberty $::env(V310_LIBERTY)
read_verilog $::env(V310_NETLIST)
link_design $::env(V310_TOP)
read_sdc $::env(V310_SDC)
puts "V310_SAME_NETLIST_ZERO_WIRE_BEGIN"
report_checks -path_delay max
puts "V310_SAME_NETLIST_ZERO_WIRE_END"
