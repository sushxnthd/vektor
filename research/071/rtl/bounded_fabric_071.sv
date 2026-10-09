// Vektor-071: bounded physical-copy router for one active transaction.
// Two independently backpressured channels; optional duplication at ingress.
// Terminal = successful egress handshake or explicitly dropped packet.
// Not a general NoC: one clock/reset domain, no external replay sources.
module bounded_fabric_071 #(
  parameter integer UID_W=4,
  parameter integer DEPTH=4
)(
  input wire clk, rst_n,
  input wire data_in_valid, output wire data_in_ready,
  input wire [UID_W-1:0] data_in_uid, input wire data_clone,
  output wire data_out_valid, input wire data_out_ready,
  output wire [UID_W-1:0] data_out_uid,
  input wire data_drop, input wire data_stall,
  input wire ack_in_valid, output wire ack_in_ready,
  input wire [UID_W-1:0] ack_in_uid, input wire ack_clone,
  output wire ack_out_valid, input wire ack_out_ready,
  output wire [UID_W-1:0] ack_out_uid,
  input wire ack_drop, input wire ack_stall,
  input wire producer_closed, input wire external_inflight,
  output wire quiescent,
  output wire [$clog2(DEPTH+1)-1:0] data_occupancy,
  output wire [$clog2(DEPTH+1)-1:0] ack_occupancy
);
  localparam integer CW=$clog2(DEPTH+1);
  localparam integer PW=(DEPTH<=2)?1:$clog2(DEPTH);
  reg [UID_W-1:0] data_mem[0:DEPTH-1], ack_mem[0:DEPTH-1];
  reg [PW-1:0] dhead, dtail, ahead, atail;
  reg [CW-1:0] dc, ac;
  wire [CW-1:0] d_push_n=data_in_valid && data_in_ready ? (data_clone ? 2 : 1) : 0;
  wire [CW-1:0] a_push_n=ack_in_valid && ack_in_ready ? (ack_clone ? 2 : 1) : 0;
  wire dpop=(dc!=0) && !data_stall && (data_drop || data_out_ready);
  wire apop=(ac!=0) && !ack_stall && (ack_drop || ack_out_ready);
  function automatic [PW-1:0] step(input [PW-1:0] pos, input integer n);
    integer v;
    begin v=pos+n; if(v>=DEPTH) v=v-DEPTH; step=v[PW-1:0]; end
  endfunction
  assign data_in_ready=(dc + (data_clone ? 2 : 1) <= DEPTH);
  assign ack_in_ready=(ac + (ack_clone ? 2 : 1) <= DEPTH);
  assign data_out_valid=(dc!=0) && !data_stall && !data_drop;
  assign ack_out_valid=(ac!=0) && !ack_stall && !ack_drop;
  assign data_out_uid=data_mem[dhead];
  assign ack_out_uid=ack_mem[ahead];
  assign data_occupancy=dc;
  assign ack_occupancy=ac;
  // Closure of both producers plus empty physical queues, not merely an ACK.
  assign quiescent=producer_closed && !external_inflight &&
                    dc==0 && ac==0 && !data_in_valid && !ack_in_valid;
  always @(posedge clk or negedge rst_n) begin
    if(!rst_n) begin
      dhead<=0; dtail<=0; ahead<=0; atail<=0; dc<=0; ac<=0;
    end else begin
      if(d_push_n!=0) begin
        data_mem[dtail]<=data_in_uid;
        if(data_clone) data_mem[step(dtail,1)]<=data_in_uid;
        dtail<=step(dtail,d_push_n);
      end
      if(a_push_n!=0) begin
        ack_mem[atail]<=ack_in_uid;
        if(ack_clone) ack_mem[step(atail,1)]<=ack_in_uid;
        atail<=step(atail,a_push_n);
      end
      if(dpop) dhead<=step(dhead,1);
      if(apop) ahead<=step(ahead,1);
      dc<=dc+d_push_n-(dpop?1:0);
      ac<=ac+a_push_n-(apop?1:0);
    end
  end
endmodule
