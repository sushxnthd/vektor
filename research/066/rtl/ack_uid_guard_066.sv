// Vektor-066: ACK identity guard and stable retirement.
// Requires immutable transaction IDs unique across maximum ACK replay lifetime.
// closed_quiescent must certify closed DATA generation and zero physical copies.
// Neither premise is proven by this component.
module ack_uid_guard_066 #(parameter TAG_W=4, UID_W=16)(
 input wire clk, rst_n,
 input wire alloc_valid, output wire alloc_ready,
 input wire [TAG_W-1:0] alloc_tag,
 input wire [UID_W-1:0] alloc_uid,
 input wire ack_in_valid, output wire ack_in_ready,
 input wire [TAG_W-1:0] ack_in_tag,
 input wire [UID_W-1:0] ack_in_uid,
 input wire closed_quiescent,
 output wire retire_valid, input wire retire_ready,
 output wire [TAG_W-1:0] retire_tag,
 output wire [UID_W-1:0] retire_uid,
 output wire stale_ack_pulse, accepted_ack_pulse
);
 reg active, ack_seen, quiescent_seen;
 reg [TAG_W-1:0] tag_q;
 reg [UID_W-1:0] uid_q;
 wire match_ack = active && (ack_in_tag == tag_q) && (ack_in_uid == uid_q);
 assign alloc_ready = !active;
 assign ack_in_ready = 1'b1;
 assign accepted_ack_pulse = ack_in_valid && match_ack;
 assign stale_ack_pulse = ack_in_valid && !match_ack;
 assign retire_valid = active && ack_seen && quiescent_seen;
 assign retire_tag = tag_q;
 assign retire_uid = uid_q;
 always @(posedge clk or negedge rst_n) begin
   if (!rst_n) begin
     active <= 0; ack_seen <= 0; quiescent_seen <= 0;
     tag_q <= 0; uid_q <= 0;
   end else if (alloc_valid && alloc_ready) begin
     active <= 1; ack_seen <= 0; quiescent_seen <= 0;
     tag_q <= alloc_tag; uid_q <= alloc_uid;
   end else if (active) begin
     if (accepted_ack_pulse) ack_seen <= 1;
     if (closed_quiescent) quiescent_seen <= 1;
     if (retire_valid && retire_ready) active <= 0;
   end
 end
endmodule
