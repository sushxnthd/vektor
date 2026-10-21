module v269_ready_select_control #(parameter W=32, parameter DEPTH=2)(
 input wire clk,rst_n,in_valid,in_class,input wire [W-1:0] in_data,
 output wire in_ready,input wire ready_slow,ready_fast,
 output wire out_valid,out_class,output wire [W-1:0] out_data,
 input wire out_ready);
 reg [W-1:0] mem[0:7]; reg cls[0:7];
 reg [3:0] count,sel;
 integer i,j;
 always @* begin
   sel=4'hf;
   for(j=0;j<DEPTH;j=j+1)
     if((j<count)&&(sel==4'hf)&&(cls[j]?ready_fast:ready_slow)) sel=j;
 end
 assign out_valid=(sel!=4'hf);
 assign out_class=out_valid?cls[sel]:1'b0;
 assign out_data=out_valid?mem[sel]:{W{1'b0}};
 assign in_ready=(count<8);
 wire pop=out_valid&&out_ready;
 wire push=in_valid&&in_ready;
 always @(posedge clk) begin
   if(!rst_n) count<=0;
   else begin
     if(pop) for(i=0;i<7;i=i+1)
       if((i>=sel)&&(i<count-1)) begin
         mem[i]<=mem[i+1];cls[i]<=cls[i+1];
       end
     if(push) begin
       mem[count-(pop?1'b1:1'b0)]<=in_data;
       cls[count-(pop?1'b1:1'b0)]<=in_class;
     end
     case({push,pop})
       2'b10:count<=count+1'b1;
       2'b01:count<=count-1'b1;
       default:;
     endcase
   end
 end
endmodule
