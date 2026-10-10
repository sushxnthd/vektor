module replay_source_072 #(
  parameter integer UID_W=4,
  parameter integer DEPTH=4
)(
  input wire clk, rst_n, fence_req, epoch_release,
  input wire source_valid, output wire source_ready,
  input wire [UID_W-1:0] source_uid,
  input wire replay_valid, output wire replay_ready,
  input wire [UID_W-1:0] replay_uid,
  output wire out_valid, input wire out_ready,
  output wire [UID_W-1:0] out_uid,
  output reg fence_ack,
  output wire [$clog2(DEPTH+1)-1:0] occupancy
);
  localparam integer CW=$clog2(DEPTH+1);
  localparam integer PW=(DEPTH<=2)?1:$clog2(DEPTH);
  reg [UID_W-1:0] mem[0:DEPTH-1];
  reg [PW-1:0] head, tail;
  reg [CW-1:0] count;
  reg closing;
  wire can_admit = !closing && !fence_req && !fence_ack &&
                   !epoch_release && (count < DEPTH);
  assign source_ready = can_admit;
  assign replay_ready = can_admit && !source_valid;
  wire push_source = source_valid && source_ready;
  wire push_replay = replay_valid && replay_ready;
  wire push = push_source || push_replay;
  wire [UID_W-1:0] push_uid = push_source ? source_uid : replay_uid;
  assign out_valid = (count != 0);
  assign out_uid = mem[head];
  wire pop = out_valid && out_ready;
  assign occupancy = count;
  function automatic [PW-1:0] advance(input [PW-1:0] pos);
    begin advance = (pos == DEPTH-1) ? {PW{1'b0}} : pos+1'b1; end
  endfunction
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      head<=0; tail<=0; count<=0; closing<=0; fence_ack<=0;
    end else begin
      if (push) begin mem[tail]<=push_uid; tail<=advance(tail); end
      if (pop) head<=advance(head);
      case ({push,pop})
        2'b10: count<=count+1'b1;
        2'b01: count<=count-1'b1;
        default: count<=count;
      endcase
      if (epoch_release && fence_ack && count==0) begin
        closing<=0;
        fence_ack<=0;
      end else begin
        if (fence_req) closing<=1;
        if ((closing || fence_req) && count==0 && !push)
          fence_ack<=1;
      end
    end
  end
endmodule
