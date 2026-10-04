module fp32_mul_frontend (
  input  logic [31:0] a,
  input  logic [31:0] b,
  output logic        special,
  output logic        sign,
  output logic signed [10:0] exp2,
  output logic [47:0] product
);
  logic [7:0] ea, eb;
  logic [22:0] fa, fb;
  logic [23:0] sa, sb;
  logic signed [10:0] qa, qb;
  always_comb begin
    ea=a[30:23]; eb=b[30:23]; fa=a[22:0]; fb=b[22:0];
    special=(ea==8'hff)||(eb==8'hff);
    sign=a[31]^b[31];
    sa=(ea==0)?{1'b0,fa}:{1'b1,fa};
    sb=(eb==0)?{1'b0,fb}:{1'b1,fb};
    qa=(ea==0)?-11'sd149:$signed({3'b000,ea})-11'sd150;
    qb=(eb==0)?-11'sd149:$signed({3'b000,eb})-11'sd150;
    exp2=qa+qb;
    product=sa*sb;
  end
endmodule
