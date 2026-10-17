# V173: matched mapped-netlist input-arrival sweep. Reuses V156 pinned library and netlists.
read_liberty $::env(VEKTOR_LIB)
read_verilog $::env(VEKTOR_NETLIST)
link_design $::env(VEKTOR_TOP)
create_clock -name core_clk -period 10 [get_ports clk]
set data_inputs [get_ports {in_valid in_tag in_mask in_product in_product_exp in_addend in_addend_exp in_product_sign in_addend_sign in_classes out_ready}]
set_input_delay $::env(VEKTOR_INPUT_DELAY_NS) -clock core_clk $data_inputs
set_output_delay 0.05 -clock core_clk [all_outputs]
set_input_transition 0.02 $data_inputs
set_load 0.01 [all_outputs]
set_false_path -from [get_ports rst_n]
puts "VEKTOR_V173_INPUT_DELAY_NS $::env(VEKTOR_INPUT_DELAY_NS)"
puts "VEKTOR_V173_TOP $::env(VEKTOR_TOP)"
report_checks -path_delay max
report_worst_slack
