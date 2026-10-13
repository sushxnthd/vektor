// V148 exact FP32 significand multiply primitive, not complete FMA.
module vektor_fp32_mul_lane (
 input wire [31:0] a,b,c,
 output wire [47:0] product,
 output wire signed [10:0] product_exp,
 output wire [23:0] addend,
 output wire signed [10:0] addend_exp,
 output wire product_sign,addend_sign,
 output wire [8:0] classes
);
 function automatic [23:0] sig(input [31:0] x);
   sig=(x[30:23]==0)?{1'b0,x[22:0]}:{1'b1,x[22:0]};
 endfunction
 function automatic signed [10:0] ex(input [31:0] x);
   ex=(x[30:23]==0)?-11'sd149:$signed({3'b000,x[30:23]})-11'sd150;
 endfunction
 function automatic [2:0] cl(input [31:0] x);
   if(x[30:23]==8'hff) cl=(x[22:0]==0)?3'd2:(x[22]?3'd3:3'd4);
   else if(x[30:0]==0) cl=3'd0;
   else cl=3'd1;
 endfunction
 assign product=sig(a)*sig(b);
 assign product_exp=ex(a)+ex(b);
 assign addend=sig(c);
 assign addend_exp=ex(c);
 assign product_sign=a[31]^b[31];
 assign addend_sign=c[31];
 assign classes={cl(c),cl(b),cl(a)};
endmodule
