module tb_rf_return_select_057;
  reg [7:0] valid;
  reg [15:0] remaining;
  reg [47:0] age;
  wire grant_valid;
  wire [7:0] grant_oh;
  wire [2:0] grant_idx;
  rf_return_select_057 dut(valid,remaining,age,grant_valid,grant_oh,grant_idx);
  initial begin
    valid=8'b00000000;remaining=0;age=0;#1;
    if (grant_valid) $stop;
    valid=8'b00000111;
    remaining=16'h0039;age=0;#1;
    if (!grant_valid) $stop;
    $finish;
  end
endmodule
