# V309 combinational issue controller: identical virtual-clock I/O constraints.
# NOT a GPU frequency target; 1 ns is a timing reference only.
create_clock -name virtual_issue_clock -period 1.0
set_input_delay -clock virtual_issue_clock 0 [all_inputs]
set_output_delay -clock virtual_issue_clock 0 [all_outputs]
set_input_transition 0.050 [all_inputs]
set_load 0.020 [all_outputs]
