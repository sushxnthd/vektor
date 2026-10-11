// V095 synchronous elastic FIFO, power-of-two depth >=2.
// No clock-domain crossing; conservative full-state pop/push policy.
module wb_elastic_fifo_095 #(
 parameter integer WIDTH=4, DEPTH=4, PTR_BITS=$clog2(DEPTH)
)(
 input wire clk,rst_n,
 input wire in_valid, output wire in_ready, input wire [WIDTH-1:0] in_data,
 output wire out_valid, input wire out_ready, output wire [WIDTH-1:0] out_data,
 output reg [PTR_BITS:0] count
);
 reg [WIDTH-1:0] mem[0:DEPTH-1];
 reg [PTR_BITS-1:0] rd,wr;
 wire push=in_valid&&in_ready;
 wire pop=out_valid&&out_ready;
 assign in_ready=(count<DEPTH);
 assign out_valid=(count!=0);
 assign out_data=mem[rd];
 always @(posedge clk or negedge rst_n) begin
  if(!rst_n) begin rd<=0;wr<=0;count<=0;end
  else begin
   if(push) begin mem[wr]<=in_data;wr<=wr+1'b1;end
   if(pop) rd<=rd+1'b1;
   case ({push,pop})
    2'b10:count<=count+1'b1;
    2'b01:count<=count-1'b1;
    default:count<=count;
   endcase
  end
 end
endmodule
