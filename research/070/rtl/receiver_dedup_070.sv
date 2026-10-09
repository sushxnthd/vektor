// Vektor-070 bounded receiver: one active transaction, finite UID,
// exactly-once logical delivery, re-ACK duplicates, explicit reuse fence.
// fence_ack is a TRUSTED external token certifying all older DATA/ACK
// physical copies terminal and no older producer can emit another copy.
module receiver_dedup_070 #(parameter integer UID_W=4) (
  input wire clk, rst_n,
  input wire start, input wire [UID_W-1:0] start_uid,
  output wire start_ready,
  input wire data_valid, input wire [UID_W-1:0] data_uid,
  output wire data_ready, output wire deliver_valid,
  output wire ack_valid, input wire ack_ready,
  output wire [UID_W-1:0] ack_uid,
  input wire retire_ok, output wire retire_valid, input wire retire_ready,
  input wire fence_ack, output wire fence_needed,
  output wire active, output wire seen
);
  reg active_q, seen_q, ack_pending_q, need_fence_q;
  reg [UID_W-1:0] uid_q;
  assign active = active_q;
  assign seen = seen_q;
  assign fence_needed = need_fence_q;
  assign start_ready = !active_q && !need_fence_q;
  assign ack_uid = uid_q;
  assign ack_valid = active_q && ack_pending_q;
  assign retire_valid = active_q && seen_q && !ack_pending_q &&
                        retire_ok && !data_valid;
  assign data_ready = active_q && data_uid == uid_q && !retire_valid;
  assign deliver_valid = data_valid && data_ready && !seen_q;
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      active_q <= 1'b0; seen_q <= 1'b0;
      ack_pending_q <= 1'b0; need_fence_q <= 1'b0;
      uid_q <= {UID_W{1'b0}};
    end else if (!active_q) begin
      if (need_fence_q && fence_ack) need_fence_q <= 1'b0;
      if (start && start_ready) begin
        active_q <= 1'b1; seen_q <= 1'b0;
        ack_pending_q <= 1'b0; uid_q <= start_uid;
      end
    end else begin
      if (data_valid && data_ready) begin
        seen_q <= 1'b1;
        ack_pending_q <= 1'b1;
      end else if (ack_valid && ack_ready) begin
        ack_pending_q <= 1'b0;
      end
      if (retire_valid && retire_ready) begin
        active_q <= 1'b0;
        need_fence_q <= 1'b1;
      end
    end
  end
endmodule
