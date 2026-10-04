module vektor_fp32_fma_align_stage (
  input  logic        prod_sign,
  input  logic signed [10:0] prod_exp2,
  input  logic [47:0] prod_sig,
  input  logic        c_sign,
  input  logic signed [10:0] c_exp2,
  input  logic [23:0] c_sig,
  output logic signed [10:0] common_exp2,
  output logic [55:0] prod_aligned,
  output logic [55:0] c_aligned,
  output logic        prod_sticky,
  output logic        c_sticky,
  output logic        out_prod_sign,
  output logic        out_c_sign
);
  logic signed [11:0] delta;
  integer sh;
  integer i;
  always_comb begin
    common_exp2 = (prod_exp2 >= c_exp2) ? prod_exp2 : c_exp2;
    prod_aligned = {8'b0, prod_sig};
    c_aligned = {32'b0, c_sig};
    prod_sticky = 1'b0;
    c_sticky = 1'b0;
    out_prod_sign = prod_sign;
    out_c_sign = c_sign;

    delta = common_exp2 - prod_exp2;
    if (delta > 0) begin
      sh = delta;
      if (sh >= 56) begin
        prod_sticky = |prod_aligned;
        prod_aligned = '0;
      end else begin
        prod_sticky = 1'b0;
        for (i = 0; i < 56; i = i + 1)
          if (i < sh) prod_sticky = prod_sticky | prod_aligned[i];
        prod_aligned = prod_aligned >> sh;
      end
    end

    delta = common_exp2 - c_exp2;
    if (delta > 0) begin
      sh = delta;
      if (sh >= 56) begin
        c_sticky = |c_aligned;
        c_aligned = '0;
      end else begin
        c_sticky = 1'b0;
        for (i = 0; i < 56; i = i + 1)
          if (i < sh) c_sticky = c_sticky | c_aligned[i];
        c_aligned = c_aligned >> sh;
      end
    end
  end
endmodule
