# V317 registered scheduler, banked dual-read flop RF proxy and operand sink.
# Typical Nangate45 only; not macro characterization or multi-corner signoff.
current_design [current_design]
create_clock -name core_clk -period 3.000 [get_ports clk]
set_clock_uncertainty 0.100 [get_clocks core_clk]
set_input_delay 0.200 -clock core_clk [get_ports {wave_valid* wave_ready* src0_bank_by_wave* src1_bank_by_wave* wr_en wr_bank* wr_row* wr_data*}]
set_output_delay 0.200 -clock core_clk [get_ports {issue_valid_sink_q* issue_wave_sink_q* operands_q* overflow_q}]
set_driving_cell -lib_cell BUF_X2 [get_ports {wave_valid* wave_ready* src0_bank_by_wave* src1_bank_by_wave* wr_en wr_bank* wr_row* wr_data*}]
set_load 10.0 [get_ports {issue_valid_sink_q* issue_wave_sink_q* operands_q* overflow_q}]
set_false_path -from [get_ports rst_n]
