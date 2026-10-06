module tb_fp32_fma_close_accum;
  logic prod_sign, c_sign;
  logic signed [10:0] prod_lsb_exp, c_lsb_exp;
  logic [47:0] prod_sig;
  logic [23:0] c_sig;
  logic close_path;
  logic signed [10:0] common_lsb_exp;
  logic sum_sign;
  logic [48:0] sum_mag;
  logic exact_zero;

  integer fd, rc, n, errors;
  integer ps_i, cs_i, pe_i, ce_i, ss_i, z_i;
  reg [47:0] pm_i;
  reg [23:0] cm_i;
  reg [51:0] mag_i;

  vektor_fp32_fma_close_accum dut (
    .prod_sign(prod_sign), .c_sign(c_sign),
    .prod_lsb_exp(prod_lsb_exp), .c_lsb_exp(c_lsb_exp),
    .prod_sig(prod_sig), .c_sig(c_sig),
    .close_path(close_path), .common_lsb_exp(common_lsb_exp),
    .sum_sign(sum_sign), .sum_mag(sum_mag), .exact_zero(exact_zero)
  );

  initial begin
    fd = $fopen("build/rtl/close_vectors.txt", "r");
    if (fd == 0) $fatal(1, "cannot open close_vectors.txt");
    n = 0; errors = 0;
    while (!$feof(fd)) begin
      rc = $fscanf(fd, "%h %h %d %d %h %h %h %h %h\n",
                   ps_i, cs_i, pe_i, ce_i, pm_i, cm_i, ss_i, z_i, mag_i);
      if (rc == 9) begin
        prod_sign = ps_i[0]; c_sign = cs_i[0];
        prod_lsb_exp = pe_i; c_lsb_exp = ce_i;
        prod_sig = pm_i; c_sig = cm_i;
        #1;
        n = n + 1;
        if (!close_path || sum_sign !== ss_i[0] ||
            exact_zero !== z_i[0] || sum_mag !== mag_i[48:0]) begin
          errors = errors + 1;
          if (errors <= 8)
            $display("MISMATCH n=%0d close=%b sign=%b/%b zero=%b/%b mag=%h/%h pe=%0d ce=%0d",
                     n, close_path, sum_sign, ss_i[0], exact_zero, z_i[0],
                     sum_mag, mag_i[48:0], pe_i, ce_i);
        end
      end
    end
    $fclose(fd);
    if (n != 20000) $fatal(1, "expected 20000 vectors, got %0d", n);
    if (errors != 0) $fatal(1, "%0d close-path mismatches", errors);
    $display("PASS close-path RTL vectors=%0d errors=%0d", n, errors);
    $finish;
  end
endmodule
