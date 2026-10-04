module vektor_fp32_fma_mul_stage (
 input wire clk, input wire rst_n, input wire in_valid,
 input wire [31:0] a, input wire [31:0] b, input wire [31:0] c,
 output reg out_valid, output reg sign_p, output reg signed [10:0] exp_p,
 output reg [47:0] sig_p, output reg sign_c, output reg signed [10:0] exp_c,
 output reg [23:0] sig_c, output reg [2:0] class_a, output reg [2:0] class_b, output reg [2:0] class_c);
 function automatic [2:0] fpclass(input [31:0] x);
  begin
   if(x[30:23]==8'hff) fpclass=(x[22:0]==0)?3'b010:(x[22]?3'b011:3'b100);
   else if((x[30:23]==0)&&(x[22:0]==0)) fpclass=3'b000;
   else fpclass=3'b001;
  end
 endfunction
 function automatic [23:0] sig24(input [31:0] x);
  sig24=(x[30:23]==0)?{1'b0,x[22:0]}:{1'b1,x[22:0]};
 endfunction
 function automatic signed [10:0] qexp(input [31:0] x);
  begin
   if(x[30:23]==0) qexp=-11'sd149;
   else qexp=$signed({3'b000,x[30:23]})-11'sd150;
  end
 endfunction
 wire [23:0] a_sig=sig24(a);
 wire [23:0] b_sig=sig24(b);
 always @(posedge clk) begin
  if(!rst_n) begin
   out_valid<=0; sign_p<=0; exp_p<=0; sig_p<=0; sign_c<=0; exp_c<=0; sig_c<=0;
   class_a<=0; class_b<=0; class_c<=0;
  end else begin
   out_valid<=in_valid;
   if(in_valid) begin
    class_a<=fpclass(a); class_b<=fpclass(b); class_c<=fpclass(c);
    sign_p<=a[31]^b[31]; exp_p<=qexp(a)+qexp(b); sig_p<=a_sig*b_sig;
    sign_c<=c[31]; exp_c<=qexp(c); sig_c<=sig24(c);
   end
  end
 end
endmodule
