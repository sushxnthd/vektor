// V151 bounded 64-bit signed-tail FMA finisher; RNE, functional candidate only.
// Exact leading window plus signed fractional-tail correction. Not pipelined.
module vektor_fp32_bounded_prepare #(parameter integer W=64)(
 input wire product_sign,addend_sign,
 input wire signed [10:0] product_exp,addend_exp,
 input wire [47:0] product,input wire [23:0] addend,input wire [8:0] classes,
 output reg [31:0] result,output reg [4:0] fflags,
 output wire [W:0] mag_o,output wire sign_o,output wire signed [31:0] lowest_exp_o,
 output wire tail_present_o,tail_opposes_o,bypass_o
);

 reg [2:0] class_a,class_b,class_c;
 reg has_nan,has_inf_p,has_inf_c,zero_p,zero_c,invalid;
 reg [W-1:0] p_aligned,c_aligned;
 reg p_tail,c_tail,tail_present,tail_opposes,sign;
 reg signed [W:0] signed_sum;
 reg [W:0] mag;
 reg [W+1:0] round_pack;
 reg [24:0] rounded;
 reg inexact;
 integer lead_p,lead_c,exp_p,exp_c,leading_exp,lowest_exp;
 integer p_shift,c_shift,h,top_exp,k,i;
 always @* begin
  class_a=classes[2:0];class_b=classes[5:3];class_c=classes[8:6];
  has_nan=(class_a==3||class_a==4||class_b==3||class_b==4||class_c==3||class_c==4);
  has_inf_p=(class_a==2||class_b==2);
  has_inf_c=(class_c==2);
  zero_p=(class_a==0||class_b==0);
  zero_c=(class_c==0);
  invalid=(class_a==4||class_b==4||class_c==4)||
          (has_inf_p&&zero_p)||(has_inf_p&&has_inf_c&&product_sign!=addend_sign);
  result=0;fflags=0;
  p_aligned=0;c_aligned=0;p_tail=0;c_tail=0;tail_present=0;tail_opposes=0;
  signed_sum=0;mag=0;sign=0;round_pack=0;rounded=0;inexact=0;
  lead_p=-1;lead_c=-1;exp_p=-10000;exp_c=-10000;leading_exp=0;lowest_exp=0;
  p_shift=0;c_shift=0;h=-1;top_exp=0;k=0;
  if(has_nan||invalid) begin result=32'h7fc00000;fflags[4]=invalid;end
  else if(has_inf_p) result={product_sign,8'hff,23'b0};
  else if(has_inf_c) result={addend_sign,8'hff,23'b0};
  else if(product==0&&addend==0)
   result={(zero_p&&zero_c&&product_sign==addend_sign)?product_sign:1'b0,31'b0};
  else begin
   for(i=0;i<48;i=i+1) if(product[i])lead_p=i;
   for(i=0;i<24;i=i+1) if(addend[i])lead_c=i;
   if(lead_p>=0)exp_p=$signed(product_exp)+lead_p;
   if(lead_c>=0)exp_c=$signed(addend_exp)+lead_c;
   leading_exp=(exp_p>exp_c)?exp_p:exp_c;
   lowest_exp=leading_exp-(W-2);
   p_shift=$signed(product_exp)-lowest_exp;
   c_shift=$signed(addend_exp)-lowest_exp;
   if(p_shift>=0) p_aligned={{(W-48){1'b0}},product} << p_shift;
   else begin
    p_aligned={{(W-48){1'b0}},product} >> (-p_shift);
    p_tail=((p_aligned << (-p_shift)) != {{(W-48){1'b0}},product});
   end
   if(c_shift>=0) c_aligned={{(W-24){1'b0}},addend} << c_shift;
   else begin
    c_aligned={{(W-24){1'b0}},addend} >> (-c_shift);
    c_tail=((c_aligned << (-c_shift)) != {{(W-24){1'b0}},addend});
   end
   signed_sum=(product_sign ? -$signed({1'b0,p_aligned}) : $signed({1'b0,p_aligned}))+
              (addend_sign ? -$signed({1'b0,c_aligned}) : $signed({1'b0,c_aligned}));
   sign=signed_sum[W];mag=sign ? -signed_sum : signed_sum;
   tail_present=p_tail||c_tail;
   tail_opposes=p_tail ? (product_sign!=sign) : (c_tail&&(addend_sign!=sign));
   if(mag==0) result=32'h00000000;
  end
 end
 assign mag_o=mag;assign sign_o=sign;assign lowest_exp_o=lowest_exp;
 assign tail_present_o=tail_present;assign tail_opposes_o=tail_opposes;
 assign bypass_o=has_nan||invalid||has_inf_p||has_inf_c||(product==0&&addend==0)||(mag==0);
endmodule

module vektor_fp32_bounded_finish #(parameter integer W=64)(
 input wire [W:0] mag,input wire sign,input wire signed [31:0] lowest_exp,
 input wire tail_present,tail_opposes,bypass,
 input wire [31:0] bypass_result,input wire [4:0] bypass_fflags,
 output reg [31:0] result,output reg [4:0] fflags
);
 function automatic [W+1:0] round_magnitude(
  input [W:0] m,input integer k,input tail_present,input tail_opposes
 );
  reg [W:0] floor_m,quotient;
  reg guard_bit,sticky_bit,inexact,round_up;
  integer j;
  begin
   floor_m=m-(tail_opposes ? {{W{1'b0}},1'b1} : {(W+1){1'b0}});
   quotient=0;guard_bit=0;sticky_bit=0;inexact=0;round_up=0;
   if(k<=0) begin quotient=m << (-k);inexact=tail_present; end
   else begin
    quotient=floor_m >> k;
    if(k>W+1) begin guard_bit=0;sticky_bit=(|floor_m)||tail_present;end
    else if(k==W+1) begin
     guard_bit=floor_m[W];sticky_bit=tail_present;
     for(j=0;j<W;j=j+1) if(floor_m[j])sticky_bit=1;
    end else begin
     guard_bit=floor_m[k-1];sticky_bit=tail_present;
     for(j=0;j<=W;j=j+1) if(j<k-1 && floor_m[j])sticky_bit=1;
    end
    inexact=guard_bit||sticky_bit;
    round_up=guard_bit&&(sticky_bit||quotient[0]);
    quotient=quotient+round_up;
   end
   round_magnitude={inexact,quotient};
  end
 endfunction
 reg [W+1:0] round_pack;reg [24:0] rounded;reg inexact;
 integer h,top_exp,k,i;
 always @* begin
  result=0;fflags=0;round_pack=0;rounded=0;inexact=0;
  h=-1;top_exp=0;k=0;
  if(bypass) begin result=bypass_result;fflags=bypass_fflags;end
  else begin
   if(mag==0) result=32'h00000000;
   else begin
    for(i=0;i<=W;i=i+1) if(mag[i])h=i;
    top_exp=h+lowest_exp;
    if(top_exp>=-126) begin
     k=h-23;
     round_pack=round_magnitude(mag,k,tail_present,tail_opposes);
     inexact=round_pack[W+1];rounded=round_pack[24:0];
     if(rounded[24]) begin rounded=rounded>>1;top_exp=top_exp+1;end
     if(top_exp>127) begin result={sign,8'hff,23'b0};fflags=5'b00101;end
     else begin
      result[31]=sign;result[30:23]=top_exp+127;
      result[22:0]=rounded[22:0];fflags[0]=inexact;
     end
    end else begin
     k=-149-lowest_exp;
     round_pack=round_magnitude(mag,k,tail_present,tail_opposes);
     inexact=round_pack[W+1];rounded=round_pack[24:0];
     if(rounded[23]) result={sign,8'h01,23'b0};
     else begin result={sign,8'h00,rounded[22:0]};fflags[1]=inexact;end
     fflags[0]=inexact;
    end
   end
  end
 end
endmodule
