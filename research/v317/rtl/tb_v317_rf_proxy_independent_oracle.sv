`timescale 1ns/1ps
// Independent directed RF-proxy data/port oracle. Does not compare two implementations.
// This is a functional test, not physical signoff or evidence of GPU throughput.
module tb_v317_rf_proxy_independent_oracle;
  reg clk=0; always #5 clk=~clk;
  reg wr_en=0;
  reg [3:0] wr_bank=0;
  reg [1:0] wr_row=0;
  reg [7:0] wr_data=0;
  reg [3:0] issue_valid=0;
  reg [19:0] issue_wave_flat=0;
  reg [127:0] bank0_by_wave=0, bank1_by_wave=0;
  wire [63:0] operand_data;
  wire bank_port_overflow;
  integer i;
  vektor_v317_rf_proxy_16b_2r dut(
    .clk(clk), .wr_en(wr_en), .wr_bank(wr_bank), .wr_row(wr_row),
    .wr_data(wr_data), .issue_valid(issue_valid),
    .issue_wave_flat(issue_wave_flat), .bank0_by_wave(bank0_by_wave),
    .bank1_by_wave(bank1_by_wave), .operand_data(operand_data),
    .bank_port_overflow(bank_port_overflow));
  task check;
    input [63:0] expected_data;
    input expected_overflow;
    begin
      #1;
      if (operand_data !== expected_data || bank_port_overflow !== expected_overflow) begin
        $display("FAIL data=%h expected=%h overflow=%b expected=%b",
          operand_data, expected_data, bank_port_overflow, expected_overflow);
        $fatal(1,"independent RF oracle");
      end
    end
  endtask
  initial begin
    // Initialize bank 0 rows 0..3 to 0x10..0x13.
    for (i=0;i<4;i=i+1) begin
      @(negedge clk);
      wr_en=1; wr_bank=0; wr_row=i; wr_data=8'h10+i;
    end
    @(negedge clk); wr_en=0;
    // Wave 0 reads row 0 twice, both ports of bank 0.
    issue_valid=4'b0001; issue_wave_flat=0;
    check(64'h0000000000001010, 0);
    // Wave 1 reads rows 1 and 0, distinct wave ID and same bank.
    issue_valid=4'b0010; issue_wave_flat=20'd1 << 5;
    check(64'h0000000010110000, 0);
    // Two waves require four operands from one 2R bank.
    // First wave receives two reads in bytes 0 and 1; second wave receives zeros in bytes 2 and 3; overflow asserted.
    issue_valid=4'b0011; issue_wave_flat=20'd1 << 5;
    check(64'h0000000000001010, 1);
    // No issue must not produce stale data or overflow.
    issue_valid=0;
    check(64'h0, 0);
    $display("PASS independent RF proxy read/overflow oracle");
    $finish;
  end
endmodule
