// V296 2-state SAT miter, preregistered in FORMAL_ALL_INPUT_ADMISSION_EQUIVALENCE_PREREG_20261026.md.
// These are unchanged arbitration modules; no assumptions or restricted input patterns.
// This verifies combinational admission only, NOT sequential scheduling or physical timing.
module v296_formal_miter(
  input wire [3:0] request_valid,
  input wire [15:0] bank0, bank1,
  output wire bad
);
  wire [3:0] original_grant, serial_grant, parallel_grant;
  v296_pairwise_arbiter original(
    .request_valid(request_valid), .bank0(bank0), .bank1(bank1), .grant(original_grant));
  v296_onehot_scaling #(.BANK_BITS(4), .SLOTS(4)) serial_control(
    .request_valid(request_valid), .bank0(bank0), .bank1(bank1), .grant(serial_grant));
  v296_pairwise_parallel_threshold parallel_trial(
    .request_valid(request_valid), .bank0(bank0), .bank1(bank1), .grant(parallel_grant));
  assign bad = (original_grant != serial_grant) ||
               (original_grant != parallel_grant);
endmodule

// Negative control: a realistic same-bank bug, NOT a constant inverted output.
// The deliberately incorrect variant denies slot zero when its two operands
// address the same bank. A valid same-bank request should consume both ports.
module v296_formal_mutation_miter(
  input wire [3:0] request_valid,
  input wire [15:0] bank0, bank1,
  output wire bad
);
  wire [3:0] correct_grant;
  wire [3:0] mutated_grant;
  v296_pairwise_arbiter original(
    .request_valid(request_valid), .bank0(bank0), .bank1(bank1), .grant(correct_grant));
  assign mutated_grant[3:1] = correct_grant[3:1];
  assign mutated_grant[0] = correct_grant[0] &&
                             (bank0[3:0] != bank1[3:0]);
  assign bad = (correct_grant != mutated_grant);
endmodule
