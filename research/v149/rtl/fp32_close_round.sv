module vektor_fp32_close_round (
 input wire product_sign,addend_sign,
 input wire signed [10:0] product_exp,addend_exp,
 input wire [47:0] product,
 input wire [23:0] addend,
 input wire [8:0] classes,
 output wire supported,
 output reg [31:0] result,
 output reg [4:0] fflags
);
 wire close_path,sum_sign,exact_zero;
 wire signed [10:0] common_lsb_exp;
 wire [48:0] sum_mag;
 vektor_fp32_fma_close_accum core(
  .prod_sign(product_sign),.c_sign(addend_sign),
  .prod_lsb_exp(product_exp),.c_lsb_exp(addend_exp),
  .prod_sig(product),.c_sig(addend),
  .close_path(close_path),.common_lsb_exp(common_lsb_exp),
  .sum_sign(sum_sign),.sum_mag(sum_mag),.exact_zero(exact_zero)
 );
 assign supported=close_path && classes[2:0]==3'd1 &&
                  classes[5:3]==3'd1 && classes[8:6]==3'd1;
 integer i,h,shift,top_exp;
 reg [48:0] q;
 reg [24:0] rounded;
 reg guard_bit,sticky_bit,inexact,round_up;
 always @* begin
  result=32'b0; fflags=5'b0;
  h=-1;shift=0;top_exp=0;q=0;rounded=0;
  guard_bit=0;sticky_bit=0;inexact=0;round_up=0;
  if(supported) begin
   if(exact_zero || sum_mag==0) result=32'b0;
   else begin
    for(i=0;i<49;i=i+1) if(sum_mag[i]) h=i;
    top_exp=$signed(common_lsb_exp)+h;
    if(top_exp>127) begin
     result={sum_sign,8'hff,23'b0};
     fflags=5'b00101;
    end else if(top_exp>=-126) begin
     shift=h-23;
     if(shift>0) begin
      q=sum_mag>>shift;
      guard_bit=sum_mag[shift-1];
      for(i=0;i<49;i=i+1)
       if(i<shift-1 && sum_mag[i]) sticky_bit=1'b1;
     end else q=sum_mag<<(-shift);
     inexact=guard_bit||sticky_bit;
     round_up=guard_bit&&(sticky_bit||q[0]);
     rounded={1'b0,q[23:0]}+round_up;
     if(rounded[24]) begin
      rounded=rounded>>1;
      top_exp=top_exp+1;
     end
     if(top_exp>127) begin
      result={sum_sign,8'hff,23'b0};
      fflags=5'b00101;
     end else begin
      result[31]=sum_sign;
      result[30:23]=top_exp+127;
      result[22:0]=rounded[22:0];
      fflags[0]=inexact;
     end
    end else begin
     shift=-149-$signed(common_lsb_exp);
     if(shift>49) begin
      q=0;
      sticky_bit=|sum_mag;
     end else if(shift>0) begin
      q=sum_mag>>shift;
      guard_bit=sum_mag[shift-1];
      for(i=0;i<49;i=i+1)
       if(i<shift-1 && sum_mag[i]) sticky_bit=1'b1;
     end else q=sum_mag<<(-shift);
     inexact=guard_bit||sticky_bit;
     round_up=guard_bit&&(sticky_bit||q[0]);
     rounded={1'b0,q[23:0]}+round_up;
     if(rounded[23]) result={sum_sign,8'h01,23'b0};
     else begin
      result={sum_sign,8'h00,rounded[22:0]};
      fflags[1]=inexact;
     end
     fflags[0]=inexact;
    end
   end
  end
 end
endmodule
