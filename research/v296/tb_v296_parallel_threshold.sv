`timescale 1ns/1ps
// Prospective exhaustive + independent randomized three-way arbitration check.
// Compares original V296, new equivalent V296 topology, and serial one-hot.
// No GPU performance claim follows from this purely combinational test.
module tb_v296_parallel_threshold;
  reg [3:0] request_valid;
  reg [15:0] bank0, bank1;
  wire [3:0] original_grant, trial_grant, serial_grant;
  integer code, mask, k, t, n, seed, checked, port_count [0:15];
  integer bank_a, bank_b;

  v296_pairwise_arbiter original(
    .request_valid(request_valid), .bank0(bank0), .bank1(bank1),
    .grant(original_grant));
  v296_pairwise_parallel_threshold trial(
    .request_valid(request_valid), .bank0(bank0), .bank1(bank1),
    .grant(trial_grant));
  v296_onehot_scaling #(.BANK_BITS(4), .SLOTS(4)) serial(
    .request_valid(request_valid), .bank0(bank0), .bank1(bank1),
    .grant(serial_grant));

  task check;
    begin
      if (trial_grant !== original_grant || trial_grant !== serial_grant)
        $fatal(1, "V296_PARALLEL_EQUIVALENCE_FAIL valid=%h b0=%h b1=%h orig=%h trial=%h serial=%h",
               request_valid, bank0, bank1, original_grant, trial_grant, serial_grant);
      for (integer b=0; b<16; b=b+1) port_count[b]=0;
      for (integer s=0; s<4; s=s+1) if (trial_grant[s]) begin
        if (!request_valid[s])
          $fatal(1, "V296_PARALLEL_PHANTOM_GRANT");
        bank_a=bank0[4*s +:4];
        bank_b=bank1[4*s +:4];
        port_count[bank_a]=port_count[bank_a]+1;
        port_count[bank_b]=port_count[bank_b]+1;
      end
      for (integer b=0; b<16; b=b+1)
        if (port_count[b]>2)
          $fatal(1, "V296_PARALLEL_BANK_PORT_OVERUSE bank=%0d",b);
      checked=checked+1;
    end
  endtask

  initial begin
    request_valid=0;bank0=0;bank1=0;checked=0;
    // All 3^8 ordered bank assignments, crossed with 16 validity masks.
    // Exactly 104,976 exhaustive four-request cases.
    for (code=0; code<6561; code=code+1) begin
      t=code;
      for (k=0; k<4; k=k+1) begin
        bank0[4*k +:4]=t%3; t=t/3;
        bank1[4*k +:4]=t%3; t=t/3;
      end
      for (mask=0; mask<16; mask=mask+1) begin
        request_valid=mask;
        #1;
        check();
      end
    end
    if (checked!=104976) $fatal(1, "V296_PARALLEL_INCOMPLETE_EXHAUSTIVE");

    // Full 16-bank domain, deterministic seeded random traffic.
    seed=32'h2960cafe;
    for (n=0; n<60000; n=n+1) begin
      bank0=$random(seed);
      bank1=$random(seed);
      request_valid=$random(seed);
      if (n%7==0) bank1=bank0;
      if (n%11==0) begin bank0=0;bank1=0;end
      #1;
      check();
    end
    if (checked!=164976) $fatal(1, "V296_PARALLEL_INCOMPLETE_RANDOM");
    $display("V296_PARALLEL_THRESHOLD_EQUIVALENCE_PASS checks=%0d",checked);
    $finish;
  end
endmodule
