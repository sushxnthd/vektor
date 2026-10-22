// V275 E0 reference RTL; NOT simulated or synthesized yet.
// Same four slots, same waiter width, same request/retire ports.
// INDEXED=1: two 2-way sets; INDEXED=0: fully associative 4-way.
module v275_tlb_join #(parameter KEY_W=16, INDEXED=1)(
  input wire clk, rst,
  input wire req_valid,
  input wire [KEY_W-1:0] req_key,
  input wire retire_valid,
  input wire [1:0] retire_slot,
  input wire [KEY_W-1:0] retire_key,
  output wire retire_match,
  output wire [3:0] retire_waiters,
  output reg req_ready,
  output reg merged,
  output reg new_walk,
  output reg [1:0] grant_slot,
  output wire [3:0] occupied
);
  reg [KEY_W-1:0] key[0:3];
  reg [3:0] waiters[0:3];
  reg [3:0] valid;
  reg found, free_found;
  reg [1:0] hit_idx, free_idx;
  integer i;
  wire req_set = req_key[0];
  assign occupied = valid;
  assign retire_match = retire_valid && valid[retire_slot] &&
      (key[retire_slot] == retire_key);
  assign retire_waiters = retire_match ? waiters[retire_slot] : 4'b0;
  always @* begin
    found=1'b0; free_found=1'b0;
    hit_idx=2'b0; free_idx=2'b0;
    for (integer j=0;j<4;j=j+1) begin
      if (!INDEXED || (j>=2)==req_set) begin
        if (!found && valid[j] && key[j]==req_key) begin
          found=1'b1; hit_idx=j[1:0];
        end
        if (!free_found && !valid[j]) begin
          free_found=1'b1; free_idx=j[1:0];
        end
      end
    end
    req_ready=1'b0; merged=1'b0; new_walk=1'b0;
    grant_slot=2'b0;
    if (req_valid && !retire_valid) begin
      if (found && waiters[hit_idx]!=4'hf) begin
        req_ready=1'b1; merged=1'b1; grant_slot=hit_idx;
      end else if (!found && free_found) begin
        req_ready=1'b1; new_walk=1'b1; grant_slot=free_idx;
      end
    end
  end
  always @(posedge clk) begin
    if (rst) begin
      valid <= 4'b0;
      for (i=0;i<4;i=i+1) begin
        key[i] <= {KEY_W{1'b0}};
        waiters[i] <= 4'b0;
      end
    end else begin
      if (retire_match) valid[retire_slot] <= 1'b0;
      if (req_ready) begin
        if (new_walk) begin
          valid[grant_slot] <= 1'b1;
          key[grant_slot] <= req_key;
          waiters[grant_slot] <= 4'd1;
        end else if (merged) begin
          waiters[grant_slot] <= waiters[grant_slot]+4'd1;
        end
      end
    end
  end
endmodule
