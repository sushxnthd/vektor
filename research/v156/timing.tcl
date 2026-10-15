# V156 matched, unplaced, single-corner standard-cell STA.
# Ubuntu 22.04 OpenSTA 2.0.17-compatible syntax.
# Not physical timing, routed Fmax, power, or GPU performance.
read_liberty $::env(VEKTOR_LIB)
read_verilog $::env(VEKTOR_NETLIST)
link_design $::env(VEKTOR_TOP)
create_clock -name core_clk -period 10 [get_ports clk]
set data_inputs [get_ports {in_valid in_tag in_mask in_product in_product_exp in_addend in_addend_exp in_product_sign in_addend_sign in_classes out_ready}]
set_input_delay 0.05 -clock core_clk $data_inputs
set_output_delay 0.05 -clock core_clk [all_outputs]
set_input_transition 0.02 $data_inputs
set_load 0.01 [all_outputs]
set_false_path -from [get_ports rst_n]
puts "VEKTOR_STA_MODE $::env(VEKTOR_TOP)"
puts "VEKTOR_STA_CONSTRAINT clock_period_ns=10 input_delay_ns=0.05 output_delay_ns=0.05 input_transition_ns=0.02 output_load=0.01"
report_checks -path_delay max
report_worst_slack
