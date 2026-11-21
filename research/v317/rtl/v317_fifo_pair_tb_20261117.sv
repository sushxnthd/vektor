// Exhaustive 2-bit-bank functional check of strict FIFO reference.
// Run: iverilog -g2012 -s v317_fifo_pair_tb -o /tmp/v317_tb \
//   research/v317/rtl/v317_fifo_pair_reference_20261117.sv \
//   research/v317/rtl/v317_fifo_pair_tb_20261117.sv && vvp /tmp/v317_tb
// Requires Icarus Verilog; no physical timing or power conclusions.
module v317_fifo_pair_tb;
  reg head_valid, next_valid, downstream_ready;
  reg [1:0] head_bank, next_bank;
  wire issue_head, issue_next;
  integer h,n,r,b0,b1,tests;
  reg expected_head, expected_next;
  v317_fifo_pair_reference #(.BANK_BITS(2)) dut(
    .head_valid(head_valid), .head_bank(head_bank),
    .next_valid(next_valid), .next_bank(next_bank),
    .downstream_ready(downstream_ready),
    .issue_head(issue_head), .issue_next(issue_next));
  initial begin
    tests=0;
    for(h=0;h<2;h=h+1)
    for(n=0;n<2;n=n+1)
    for(r=0;r<2;r=r+1)
    for(b0=0;b0<4;b0=b0+1)
    for(b1=0;b1<4;b1=b1+1) begin
      head_valid=h; next_valid=n; downstream_ready=r;
      head_bank=b0; next_bank=b1;
      #1;
      expected_head=(h!=0)&&(r!=0);
      expected_next=expected_head&&(n!=0)&&(b0!=b1);
      if(issue_head !== expected_head || issue_next !== expected_next) begin
        $display("FAIL h=%0d n=%0d r=%0d b0=%0d b1=%0d",h,n,r,b0,b1);
        $fatal(1);
      end
      if(issue_next && !issue_head) $fatal(1,"FIFO order violation");
      if(issue_next && head_bank==next_bank) $fatal(1,"bank collision");
      tests=tests+1;
    end
    if(tests!=128) $fatal(1,"incomplete enumeration");
    $display("PASS %0d exhaustive binary-valid/ready, four-bank combinations",tests);
    $finish;
  end
endmodule
