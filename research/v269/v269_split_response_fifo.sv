module v269_split_response_fifo #(parameter integer W=32)(
 input wire clk,rst_n,in_valid,in_class,input wire [W-1:0] in_data,
 output wire in_ready,input wire ready_slow,ready_fast,
 output wire out_valid,out_class,output wire [W-1:0] out_data,input wire out_ready
);
 reg [W-1:0] slow_mem[0:3],fast_mem[0:3];
 reg [1:0] slow_rd,slow_wr,fast_rd,fast_wr;
 reg [2:0] slow_count,fast_count;
 reg rr;
 wire slow_ok=(slow_count!=0)&&ready_slow;
 wire fast_ok=(fast_count!=0)&&ready_fast;
 wire choose_fast=fast_ok&&(!slow_ok||rr);
 assign out_valid=slow_ok||fast_ok;
 assign out_class=choose_fast;
 assign out_data=choose_fast?fast_mem[fast_rd]:slow_mem[slow_rd];
 assign in_ready=in_class?(fast_count<4):(slow_count<4);
 wire push_slow=in_valid&&in_ready&&!in_class;
 wire push_fast=in_valid&&in_ready&&in_class;
 wire pop_slow=out_valid&&out_ready&&!choose_fast;
 wire pop_fast=out_valid&&out_ready&&choose_fast;
 always @(posedge clk) begin
  if(!rst_n) begin
   slow_rd<=0;slow_wr<=0;fast_rd<=0;fast_wr<=0;
   slow_count<=0;fast_count<=0;rr<=0;
  end else begin
   if(push_slow) begin slow_mem[slow_wr]<=in_data;slow_wr<=slow_wr+1'b1;end
   if(push_fast) begin fast_mem[fast_wr]<=in_data;fast_wr<=fast_wr+1'b1;end
   if(pop_slow) slow_rd<=slow_rd+1'b1;
   if(pop_fast) fast_rd<=fast_rd+1'b1;
   case({push_slow,pop_slow})
    2'b10:slow_count<=slow_count+1'b1;
    2'b01:slow_count<=slow_count-1'b1;
    default: ;
   endcase
   case({push_fast,pop_fast})
    2'b10:fast_count<=fast_count+1'b1;
    2'b01:fast_count<=fast_count-1'b1;
    default: ;
   endcase
   if(out_valid&&out_ready) rr<=!choose_fast;
  end
 end
endmodule
