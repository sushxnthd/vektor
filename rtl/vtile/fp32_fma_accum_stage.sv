module vektor_fp32_fma_accum_stage (
  input  logic        prod_sign,
  input  logic        c_sign,
  input  logic [55:0] prod_aligned,
  input  logic [55:0] c_aligned,
  output logic        sum_sign,
  output logic [56:0] sum_mag,
  output logic        exact_zero
);
  logic [56:0] p_ext, c_ext;
  always_comb begin
    p_ext = {1'b0, prod_aligned};
    c_ext = {1'b0, c_aligned};
    sum_sign = 1'b0; sum_mag = '0; exact_zero = 1'b0;
    if (prod_sign == c_sign) begin
      sum_mag = p_ext + c_ext;
      sum_sign = prod_sign;
      exact_zero = (sum_mag == 0);
    end else if (p_ext > c_ext) begin
      sum_mag = p_ext - c_ext; sum_sign = prod_sign;
    end else if (c_ext > p_ext) begin
      sum_mag = c_ext - p_ext; sum_sign = c_sign;
    end else begin
      sum_mag = '0; sum_sign = 1'b0; exact_zero = 1'b1;
    end
  end
endmodule
