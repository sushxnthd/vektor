module vektor_fp32_fma_close_accum (
  input  logic        prod_sign,
  input  logic        c_sign,
  input  logic signed [10:0] prod_lsb_exp,
  input  logic signed [10:0] c_lsb_exp,
  input  logic [47:0] prod_sig,
  input  logic [23:0] c_sig,
  output logic        close_path,
  output logic signed [10:0] common_lsb_exp,
  output logic        sum_sign,
  output logic [48:0] sum_mag,
  output logic        exact_zero
);
  logic signed [11:0] d;
  logic [48:0] p, c;

  always_comb begin
    d = prod_lsb_exp - c_lsb_exp;
    close_path = (d >= -1) && (d <= 1);
    common_lsb_exp = (prod_lsb_exp < c_lsb_exp) ? prod_lsb_exp : c_lsb_exp;
    p = {1'b0, prod_sig};
    c = {25'b0, c_sig};

    // In the close regime only one operand can require a one-bit exact
    // left shift.  49 bits therefore preserve every cancellation bit.
    if (close_path) begin
      if (d == 1)
        p = {prod_sig, 1'b0};
      else if (d == -1)
        c = {24'b0, c_sig, 1'b0};
    end

    sum_sign = 1'b0;
    sum_mag = '0;
    exact_zero = 1'b0;
    if (!close_path) begin
      sum_mag = '0; // caller must select the far path
    end else if (prod_sign == c_sign) begin
      sum_mag = p + c;
      sum_sign = prod_sign;
      exact_zero = (sum_mag == 0);
    end else if (p > c) begin
      sum_mag = p - c;
      sum_sign = prod_sign;
    end else if (c > p) begin
      sum_mag = c - p;
      sum_sign = c_sign;
    end else begin
      exact_zero = 1'b1;
    end
  end
endmodule
