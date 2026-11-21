# V317 matched registered arbiter boundary; Nangate45 timing units ns, capacitance fF.
# No GPU clock-frequency claim. Same constraints for both physical variants.
current_design [current_design]
create_clock -name core_clk -period 2.000 [get_ports clk]
set_clock_uncertainty 0.100 [get_clocks core_clk]
set_input_delay 0.200 -clock core_clk [get_ports {request_valid* src0_bank_flat* src1_bank_flat*}]
set_output_delay 0.200 -clock core_clk [get_ports {grant*}]
set_driving_cell -lib_cell BUF_X2 [get_ports {request_valid* src0_bank_flat* src1_bank_flat*}]
set_load 10.0 [get_ports {grant*}]
