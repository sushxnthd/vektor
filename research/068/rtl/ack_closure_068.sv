// Vektor-068: bounded one-transaction physical-replica accounting.
// Send creates a copy, clone adds a physical copy, terminal destroys one.
// A delivery is a terminal. Closure stops NEW sends, not in-flight clones.
// A late ACK after producer closure is legal; all replicas must terminate.
// fabric_quiescent is a trusted external reset fence, NOT proved here.
module ack_closure_068 #(parameter COUNT_W=4) (
  input wire clk, rst_n, fabric_quiescent,
  input wire start, output wire start_ready,
  input wire data_send, data_clone, data_terminal, data_deliver, data_close,
  output wire ack_valid, input wire ack_ready,
  input wire ack_clone, ack_terminal, ack_deliver,
  output wire ack_closed, output wire retire_valid, input wire retire_ready,
  output reg protocol_error,
  output wire [COUNT_W-1:0] data_pending, ack_pending, ack_queued
);
  reg active, fenced, data_closed_q, ack_closed_q, ack_seen;
  reg [COUNT_W-1:0] d, a, q;
  localparam [COUNT_W-1:0] MAX = {COUNT_W{1'b1}};
  wire ack_send = ack_valid && ack_ready;
  wire [COUNT_W+1:0] dn = {2'b0,d} + data_send + data_clone - data_terminal;
  wire [COUNT_W+1:0] an = {2'b0,a} + ack_send + ack_clone - ack_terminal;
  wire [COUNT_W+1:0] qn = {2'b0,q} + data_deliver - ack_send;
  wire bad_d = (data_send && data_closed_q) ||
      (data_clone && d == 0) || (data_terminal && d == 0 && !data_send) ||
      (data_deliver && !data_terminal) || (data_close && data_send) ||
      (dn > {2'b00,MAX});
  wire bad_a = (ack_clone && a == 0) ||
      (ack_terminal && a == 0 && !ack_send) ||
      (ack_deliver && !ack_terminal) || (an > {2'b00,MAX});
  wire bad_q = (qn > {2'b00,MAX});
  assign start_ready = !active && fenced && !protocol_error;
  assign ack_valid = active && q != 0 && !protocol_error;
  assign ack_closed = active && ack_closed_q;
  assign retire_valid = active && ack_seen && ack_closed_q &&
                        d == 0 && a == 0 && q == 0 && !protocol_error;
  assign data_pending = d;
  assign ack_pending = a;
  assign ack_queued = q;
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      active <= 0; fenced <= 0; data_closed_q <= 0;
      ack_closed_q <= 0; ack_seen <= 0; protocol_error <= 0;
      d <= 0; a <= 0; q <= 0;
    end else if (!active) begin
      if (fabric_quiescent) begin fenced <= 1; protocol_error <= 0; end
      if (start && start_ready) begin
        active <= 1; data_closed_q <= 0; ack_closed_q <= 0;
        ack_seen <= 0; d <= 0; a <= 0; q <= 0;
      end
    end else begin
      if (bad_d || bad_a || bad_q || (ack_closed_q && data_deliver))
        protocol_error <= 1;
      else begin
        d <= dn[COUNT_W-1:0];
        a <= an[COUNT_W-1:0];
        q <= qn[COUNT_W-1:0];
        if (data_close) data_closed_q <= 1;
        if (ack_deliver) ack_seen <= 1;
        if (data_closed_q && d == 0 && q == 0 && !data_send &&
            !data_clone && !data_terminal && !data_deliver)
          ack_closed_q <= 1;
        if (retire_valid && retire_ready) active <= 0;
      end
    end
  end
endmodule
