// V287 physicality gate: deterministic exhaustive mask and randomized operand checks.
// Compare fused writeback against two sequential baseline issues.
module tb_v287;
  reg [7:0] mask_a, mask_b;
  reg [1:0] op_a, op_b;
  reg [255:0] lhs_a, rhs_a, lhs_b, rhs_b;
  reg [95:0] dst_a, dst_b;
  wire fused, ra, rb;
  wire [7:0] wen;
  wire [255:0] wdata;
  wire [95:0] waddr;
  wire ca_f, ca_ra, ca_rb, cb_f, cb_ra, cb_rb;
  wire [7:0] wa, wb;
  wire [255:0] da, db;
  wire [95:0] aa, ab;
  integer i,j,k,tests, pairs;
  reg expect_f;
  v287_lane_fuse_phys dut(
    .mask_a(mask_a),.mask_b(mask_b),.op_a(op_a),.op_b(op_b),
    .lhs_a(lhs_a),.rhs_a(rhs_a),.lhs_b(lhs_b),.rhs_b(rhs_b),
    .dst_a(dst_a),.dst_b(dst_b),
    .fused(fused),.retire_a(ra),.retire_b(rb),
    .wen(wen),.wdata(wdata),.waddr(waddr)
  );
  v287_lane_control ctrl_a(
    .mask_a(mask_a),.mask_b(mask_b),.op_a(op_a),.op_b(op_b),
    .lhs_a(lhs_a),.rhs_a(rhs_a),.lhs_b(lhs_b),.rhs_b(rhs_b),
    .dst_a(dst_a),.dst_b(dst_b),
    .fused(ca_f),.retire_a(ca_ra),.retire_b(ca_rb),
    .wen(wa),.wdata(da),.waddr(aa)
  );
  v287_lane_control ctrl_b(
    .mask_a(mask_b),.mask_b(mask_a),.op_a(op_b),.op_b(op_a),
    .lhs_a(lhs_b),.rhs_a(rhs_b),.lhs_b(lhs_a),.rhs_b(rhs_a),
    .dst_a(dst_b),.dst_b(dst_a),
    .fused(cb_f),.retire_a(cb_ra),.retire_b(cb_rb),
    .wen(wb),.wdata(db),.waddr(ab)
  );
  task verify;
  begin
    #1;
    expect_f = (|mask_a) && (|mask_b) && (op_a==0) && (op_b==0) &&
               ((mask_a & mask_b)==0);
    if (fused !== expect_f || ra !== ca_ra || rb !== expect_f) begin
      $display("FAIL retirement ma=%h mb=%h oa=%h ob=%h",mask_a,mask_b,op_a,op_b);
      $fatal(1);
    end
    for (k=0;k<8;k=k+1) begin
      if (expect_f && mask_b[k]) begin
        if (wen[k] !== wb[k] ||
            wdata[k*32+:32] !== db[k*32+:32] ||
            waddr[k*12+:12] !== ab[k*12+:12]) begin
          $display("FAIL B lane=%0d ma=%h mb=%h",k,mask_a,mask_b);
          $fatal(1);
        end
      end else begin
        if (wen[k] !== wa[k] ||
            (wa[k] && (wdata[k*32+:32] !== da[k*32+:32] ||
                       waddr[k*12+:12] !== aa[k*12+:12]))) begin
          $display("FAIL A lane=%0d ma=%h mb=%h",k,mask_a,mask_b);
          $fatal(1);
        end
      end
    end
    tests=tests+1;
    if (expect_f) pairs=pairs+1;
  end
  endtask
  initial begin
    tests=0;pairs=0;
    // Freeze all mask-pair cases before reading workload holdouts.
    op_a=0;op_b=0;
    for (i=0;i<8;i=i+1) begin
      lhs_a[i*32+:32]=$random;rhs_a[i*32+:32]=$random;
      lhs_b[i*32+:32]=$random;rhs_b[i*32+:32]=$random;
      dst_a[i*12+:12]=$random;dst_b[i*12+:12]=$random;
    end
    for(i=0;i<256;i=i+1) begin
      for(j=0;j<256;j=j+1) begin
        mask_a=i;mask_b=j;
        verify();
      end
    end
    for(i=0;i<30000;i=i+1) begin
      mask_a=$random;mask_b=$random;op_a=$random;op_b=$random;
      for (j=0;j<8;j=j+1) begin
        lhs_a[j*32+:32]=$random;rhs_a[j*32+:32]=$random;
        lhs_b[j*32+:32]=$random;rhs_b[j*32+:32]=$random;
        dst_a[j*12+:12]=$random;dst_b[j*12+:12]=$random;
      end
      verify();
    end
    $display("V287 PASS cases=%0d fused_cases=%0d",tests,pairs);
    $finish;
  end
endmodule
