// V150 functional full-range binary32 FMA reference, RNE only.
// Exact 555-bit dyadic alignment: verification baseline, NOT a high-performance design.
module vektor_fp32_full_reference (
 input wire product_sign,addend_sign,
 input wire signed [10:0] product_exp,addend_exp,
 input wire [47:0] product,input wire [23:0] addend,
 input wire [8:0] classes,output reg [31:0] result,output reg [4:0] fflags
);
 localparam integer W=555;
 reg [W-1:0] p_aligned,c_aligned,mag,q;
 reg signed [W:0] signed_sum;
 reg [24:0] rounded;
 reg sign,guard_bit,sticky_bit,inexact,round_up;
 reg invalid,has_nan,has_inf_p,has_inf_c,zero_p,zero_c;
 integer p_shift,c_shift,h,top_exp,shift,i;
 reg [2:0] ca,cb,cc;
 always @* begin
  ca=classes[2:0];cb=classes[5:3];cc=classes[8:6];
  has_nan=(ca==3 || ca==4 || cb==3 || cb==4 || cc==3 || cc==4);
  has_inf_p=(ca==2 || cb==2);has_inf_c=(cc==2);
  zero_p=(ca==0 || cb==0);zero_c=(cc==0);
  invalid=(ca==4 || cb==4 || cc==4) ||
          (has_inf_p && zero_p) ||
          (has_inf_p && has_inf_c && (product_sign!=addend_sign));
  result=0;fflags=0;p_aligned=0;c_aligned=0;mag=0;signed_sum=0;
  rounded=0;q=0;sign=0;guard_bit=0;sticky_bit=0;
  inexact=0;round_up=0;p_shift=0;c_shift=0;h=-1;top_exp=0;shift=0;
  if(has_nan || invalid) begin
   result=32'h7fc00000;fflags[4]=invalid;
  end else if(has_inf_p) begin
   result={product_sign,8'hff,23'b0};
  end else if(has_inf_c) begin
   result={addend_sign,8'hff,23'b0};
  end else begin
   // All finite product shifts 0..506; addend shifts 149..402.
   // Largest product bit is 553, and same-sign addition may reach 554.
   p_shift=$signed(product_exp)+298;
   c_shift=$signed(addend_exp)+298;
   p_aligned={{(W-48){1'b0}},product} << p_shift;
   c_aligned={{(W-24){1'b0}},addend} << c_shift;
   signed_sum=(product_sign ? -$signed({1'b0,p_aligned}) : $signed({1'b0,p_aligned})) +
              (addend_sign ? -$signed({1'b0,c_aligned}) : $signed({1'b0,c_aligned}));
   sign=signed_sum[W];mag=sign ? -signed_sum : signed_sum;
   if(mag==0) begin
    result={(zero_p && zero_c && product_sign==addend_sign) ? product_sign : 1'b0,31'b0};
   end else begin
    for(i=0;i<W;i=i+1) if(mag[i]) h=i;
    top_exp=h-298;
    if(top_exp>=-126) begin
     shift=h-23;
     if(shift>0) begin
      q=mag>>shift;guard_bit=mag[shift-1];
      for(i=0;i<W;i=i+1) if(i<shift-1 && mag[i]) sticky_bit=1'b1;
     end else q=mag<<(-shift);
     inexact=guard_bit||sticky_bit;
     round_up=guard_bit&&(sticky_bit||q[0]);
     rounded={1'b0,q[23:0]}+round_up;
     if(rounded[24]) begin rounded=rounded>>1;top_exp=top_exp+1;end
     if(top_exp>127) begin
      result={sign,8'hff,23'b0};fflags=5'b00101;
     end else begin
      result[31]=sign;result[30:23]=top_exp+127;result[22:0]=rounded[22:0];
      fflags[0]=inexact;
     end
    end else begin
     // Subnormal RNE at fixed exact-dyadic shift 149.
     shift=149;q=mag>>shift;guard_bit=mag[shift-1];
     for(i=0;i<W;i=i+1) if(i<shift-1 && mag[i]) sticky_bit=1'b1;
     inexact=guard_bit||sticky_bit;
     round_up=guard_bit&&(sticky_bit||q[0]);
     rounded={1'b0,q[23:0]}+round_up;
     if(rounded[23]) result={sign,8'h01,23'b0};
     else begin
      result={sign,8'h00,rounded[22:0]};fflags[1]=inexact;
     end
     fflags[0]=inexact;
    end
   end
  end
 end
endmodule
