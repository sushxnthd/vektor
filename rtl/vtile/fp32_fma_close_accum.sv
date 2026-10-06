module vektor_fp32_fma_close_accum (
  input logic prod_sign, input logic c_sign,
  input logic signed [10:0] prod_lsb_exp, input logic signed [10:0] c_lsb_exp,
  input logic [47:0] prod_sig, input logic [23:0] c_sig,
  output logic close_path, output logic signed [10:0] common_lsb_exp,
  output logic sum_sign, output logic [48:0] sum_mag, output logic exact_zero
);
  integer i; integer lp; integer lc; integer sh;
  logic signed [12:0] prod_lead_exp, c_lead_exp, lead_delta;
  logic [48:0] p, c;

  always_comb begin
    lp = -1; lc = -1;
    for (i=0; i<48; i=i+1) if (prod_sig[i]) lp=i;
    for (i=0; i<24; i=i+1) if (c_sig[i]) lc=i;
    prod_lead_exp = $signed(prod_lsb_exp) + lp;
    c_lead_exp = $signed(c_lsb_exp) + lc;
    lead_delta = prod_lead_exp - c_lead_exp;
    close_path = (lp >= 0) && (lc >= 0) && (lead_delta >= -1) && (lead_delta <= 1);
    common_lsb_exp = (prod_lsb_exp < c_lsb_exp) ? prod_lsb_exp : c_lsb_exp;
    p = {1'b0,prod_sig}; c = {25'b0,c_sig};
    if (close_path) begin
      if (prod_lsb_exp > common_lsb_exp) begin
        sh = prod_lsb_exp-common_lsb_exp; p = p << sh;
      end
      if (c_lsb_exp > common_lsb_exp) begin
        sh = c_lsb_exp-common_lsb_exp; c = c << sh;
      end
    end
    sum_sign=0; sum_mag=0; exact_zero=0;
    if (close_path) begin
      if (prod_sign==c_sign) begin sum_mag=p+c; sum_sign=prod_sign; exact_zero=(p+c)==0; end
      else if (p>c) begin sum_mag=p-c; sum_sign=prod_sign; end
      else if (c>p) begin sum_mag=c-p; sum_sign=c_sign; end
      else exact_zero=1;
    end
  end
endmodule
