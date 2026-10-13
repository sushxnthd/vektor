# V156 matched, unplaced, single-corner standard-cell STA.
# Does NOT model placement, wire parasitics, clock-tree skew, power, or routing.
read_liberty $::env(VEKTOR_LIB)
read_verilog $::env(VEKTOR_NETLIST)
link_design $::env(VEKTOR_TOP)
create_clock -name core_clk -period 10 [get_ports clk]
set_input_delay 0.05 -clock core_clk [all_inputs -no_clocks]
set_output_delay 0.05 -clock core_clk [all_outputs]
set_input_transition 0.02 [all_inputs -no_clocks]
set_load 0.01 [all_outputs]
set_false_path -from [get_ports rst_n]
puts "VEKTOR_STA_MODE $::env(VEKTOR_TOP)"
puts "VEKTOR_STA_CONSTRAINT clock_period_ns=10 input_delay_ns=0.05 output_delay_ns=0.05 input_transition_ns=0.02 output_load=0.01"
report_checks -path_delay max -group_path_count 5
report_worst_slack -max
