# Frozen V198 symbolic wire-load stress protocol

Inputs: archived V196 control/cutset mapped netlists for repair headrooms 0, 10, 20, 30 percent, and the archived Nangate45 typical Liberty. For each output cell with max_capacitance and N directly connected input pins, let C_pin be the sum of input-pin capacitances.

For a uniform *hypothetical* wire capacitance w per sink, define C_total(w) = C_pin + N*w. The first violating threshold for each driver with N>0 is w* = (C_max - C_pin)/N. The design's boundary is min(w*) over eligible drivers. Count violating drivers at w = 0, 0.05, 0.1, 0.25, 0.5, 1, 2, 4 fF per sink. Compare control/cutset under identical stress.

The model excludes physical parasitic extraction, top-level output loads, alias-resolved loads, coupling, transition, placement and routing. These omissions must not be presented as a measured physical effect. Verify using a second parser with independent source code.
