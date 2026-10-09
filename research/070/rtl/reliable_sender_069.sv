// Vektor-069 experimental retry sender copied for 070 integration.
// Physical terminal accounting, UID reuse and fence certification external.
module reliable_sender_069 #(
  parameter integer UID_W=16, TIMEOUT_CYCLES=8, RETRY_W=16
)(
  input wire clk, rst_n, fabric_quiescent,
  input wire start, input wire [UID_W-1:0] start_uid,
  output wire start_ready, output wire data_valid,
  input wire data_ready, output wire [UID_W-1:0] data_uid,
  input wire ack_valid, input wire [UID_W-1:0] ack_uid,
  output wire sender_closed, input wire fabric_retired,
  output wire [RETRY_W-1:0] retry_count
);
  localparam integer TIMER_W = TIMEOUT_CYCLES <= 1 ? 1 : $clog2(TIMEOUT_CYCLES);
  reg active_q, pending_q, issued_q, closed_q;
  reg [UID_W-1:0] uid_q;
  reg [TIMER_W-1:0] timer_q;
  reg [RETRY_W-1:0] retries_q;
  wire ack_match = active_q && issued_q && ack_valid && ack_uid == uid_q;
  assign start_ready = !active_q && fabric_quiescent;
  assign data_valid = active_q && pending_q && !closed_q;
  assign data_uid = uid_q;
  assign sender_closed = active_q && closed_q;
  assign retry_count = retries_q;
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      active_q<=0; pending_q<=0; issued_q<=0; closed_q<=0;
      uid_q<=0; timer_q<=0; retries_q<=0;
    end else if (start && start_ready) begin
      active_q<=1; pending_q<=1; issued_q<=0; closed_q<=0;
      uid_q<=start_uid; timer_q<=0; retries_q<=0;
    end else if (active_q) begin
      if (closed_q && fabric_retired) begin
        active_q<=0; pending_q<=0;
      end else if (ack_match) begin
        closed_q<=1; pending_q<=0;
      end else if (!closed_q) begin
        if (pending_q) begin
          if (data_ready) begin
            pending_q<=0; timer_q<=0;
            if (issued_q) retries_q<=retries_q+1'b1;
            issued_q<=1;
          end
        end else if (timer_q == TIMEOUT_CYCLES-1) begin
          pending_q<=1; timer_q<=0;
        end else timer_q<=timer_q+1'b1;
      end
    end
  end
endmodule
