// V257 experimental 4-bank x 4-entry response buffer. No physical claim.
// MODE 0: fixed, 1: ring two-choice, 2: pooled. All have 4 ingress,
// 4 output, 16 entries, and one read/one write per bank each cycle.
module v257_response_buffer #(
 parameter integer MODE=0, ID_W=8, DATA_W=32
)(
 input wire clk, rst,
 input wire [3:0] in_valid,
 input wire [7:0] in_home,
 input wire [4*ID_W-1:0] in_id,
 input wire [4*DATA_W-1:0] in_data,
 output reg [3:0] in_ready,
 output wire [3:0] out_valid,
 output wire [4*ID_W-1:0] out_id,
 output wire [4*DATA_W-1:0] out_data,
 output wire [7:0] out_home
);
 reg [ID_W-1:0] mem_id [0:3][0:3];
 reg [DATA_W-1:0] mem_data [0:3][0:3];
 reg [1:0] mem_home [0:3][0:3];
 reg [1:0] rdptr [0:3], wrptr [0:3];
 reg [2:0] count [0:3], remaining [0:3];
 reg [3:0] used, push;
 reg [2:0] sel [0:3];
 reg [1:0] src [0:3];
 reg [2:0] best_load, score;
 reg [1:0] home;
 reg permit;
 integer lane, bank, b, k;
 always @* begin
  used=0; in_ready=0; push=0;
  for (b=0;b<4;b=b+1) begin
   remaining[b]=count[b]-(count[b]!=0);
   src[b]=0;
  end
  for (lane=0;lane<4;lane=lane+1) begin
   sel[lane]=4;
   home=in_home[lane*2 +: 2];
   best_load=5;
   if (in_valid[lane]) begin
    for (bank=0;bank<4;bank=bank+1) begin
     permit=(MODE==2)||(bank==home)||((MODE==1)&&(bank==((home+1)&3)));
     score=remaining[bank];
     if (permit && !used[bank] && score<4 &&
         ((score<best_load)||((score==best_load)&&(bank==home)))) begin
      sel[lane]=bank;
      best_load=score;
     end
    end
   end
   if (sel[lane]<4) begin
    used[sel[lane]]=1;
    remaining[sel[lane]]=remaining[sel[lane]]+1;
    push[sel[lane]]=1;
    src[sel[lane]]=lane;
    in_ready[lane]=1;
   end
  end
 end
 genvar g;
 generate for (g=0;g<4;g=g+1) begin: banks
  assign out_valid[g]=(count[g]!=0);
  assign out_id[g*ID_W +: ID_W]=mem_id[g][rdptr[g]];
  assign out_data[g*DATA_W +: DATA_W]=mem_data[g][rdptr[g]];
  assign out_home[g*2 +: 2]=mem_home[g][rdptr[g]];
 end endgenerate
 always @(posedge clk) begin
  if (rst) begin
   for (k=0;k<4;k=k+1) begin
    count[k]<=0; rdptr[k]<=0; wrptr[k]<=0;
   end
  end else begin
   for (k=0;k<4;k=k+1) begin
    if (count[k]!=0) rdptr[k]<=rdptr[k]+1;
    if (push[k]) begin
     wrptr[k]<=wrptr[k]+1;
     mem_id[k][wrptr[k]]<=in_id[src[k]*ID_W +: ID_W];
     mem_data[k][wrptr[k]]<=in_data[src[k]*DATA_W +: DATA_W];
     mem_home[k][wrptr[k]]<=in_home[src[k]*2 +: 2];
    end
    case ({push[k],(count[k]!=0)})
     2'b10:count[k]<=count[k]+1;
     2'b01:count[k]<=count[k]-1;
     default:count[k]<=count[k];
    endcase
   end
  end
 end
endmodule
