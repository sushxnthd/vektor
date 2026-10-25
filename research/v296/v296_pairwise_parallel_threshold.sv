// V296 combinational topology trial, NOT a new architecture mechanism.
// Pre-registered in PARALLEL_THRESHOLD_TOPOLOGY_PREREG_20261026.md.
// Exactly the original four-slot priority-greedy two-read-port semantics.
// Explicit cross-slot equality and >=2-hit logic replace procedural additions.
// Do not infer physical timing/area benefit without matched extracted routing.
module v296_pairwise_parallel_threshold(
  input wire [3:0] request_valid,
  input wire [15:0] bank0, bank1,
  output wire [3:0] grant
);
  // A bank has exhausted two ports iff at least two earlier granted
  // operands match it. One request contributes TWO operands, even if
  // both source banks are equal.
  function automatic two_or_more;
    input [7:0] h;
    begin
      two_or_more =
          (h[0] & (|h[7:1])) |
          (h[1] & (|h[7:2])) |
          (h[2] & (|h[7:3])) |
          (h[3] & (|h[7:4])) |
          (h[4] & (|h[7:5])) |
          (h[5] & (|h[7:6])) |
          (h[6] & h[7]);
    end
  endfunction

  wire [7:0] prior_hits_a [0:3];
  wire [7:0] prior_hits_b [0:3];
  genvar i, j;
  generate
    for (i=0; i<4; i=i+1) begin: slot
      for (j=0; j<4; j=j+1) begin: prior
        if (j<i) begin: earlier
          assign prior_hits_a[i][2*j]   = grant[j] && (bank0[4*j +:4] == bank0[4*i +:4]);
          assign prior_hits_a[i][2*j+1] = grant[j] && (bank1[4*j +:4] == bank0[4*i +:4]);
          assign prior_hits_b[i][2*j]   = grant[j] && (bank0[4*j +:4] == bank1[4*i +:4]);
          assign prior_hits_b[i][2*j+1] = grant[j] && (bank1[4*j +:4] == bank1[4*i +:4]);
        end else begin: absent
          assign prior_hits_a[i][2*j]   = 1'b0;
          assign prior_hits_a[i][2*j+1] = 1'b0;
          assign prior_hits_b[i][2*j]   = 1'b0;
          assign prior_hits_b[i][2*j+1] = 1'b0;
        end
      end
      wire same_bank;
      assign same_bank = (bank0[4*i +:4] == bank1[4*i +:4]);
      // If two operands target one bank, BOTH ports must be free.
      // Otherwise each of the two banks needs at least one free port.
      assign grant[i] = request_valid[i] &&
        (same_bank ? !(|prior_hits_a[i])
                   : !(two_or_more(prior_hits_a[i]) ||
                       two_or_more(prior_hits_b[i])));
    end
  endgenerate
endmodule
