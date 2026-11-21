# Integrated issue-control registered boundaries; typical Nangate45 ns/fF.
# Identical source/pairwise constraints. No SRAM or GPU tile in this experiment.
current_design [current_design]
create_clock -name core_clk -period 2.000 [get_ports clk]
set_clock_uncertainty 0.100 [get_clocks core_clk]
set_input_delay 0.200 -clock core_clk [get_ports {wave_valid* wave_ready* src0_bank_by_wave* src1_bank_by_wave*}]
set_output_delay 0.200 -clock core_clk [get_ports {issue_valid_q* issue_wave_flat_q*}]
set_driving_cell -lib_cell BUF_X2 [get_ports {wave_valid* wave_ready* src0_bank_by_wave* src1_bank_by_wave*}]
set_load 10.0 [get_ports {issue_valid_q* issue_wave_flat_q*}]
set_false_path -from [get_ports rst_n]
