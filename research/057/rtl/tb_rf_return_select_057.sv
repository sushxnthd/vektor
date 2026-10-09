`timescale 1ns/1ps
module tb_rf_return_select_057;
parameter integer POLICY=2;
reg [7:0] valid;
reg [15:0] remaining;
reg [47:0] age;
wire grant_valid;
wire [7:0] grant_oh;
wire [2:0] grant_idx;
rf_return_select_057 #(.POLICY(POLICY)) dut(
  .valid(valid),.remaining(remaining),.age(age),
  .grant_valid(grant_valid),.grant_oh(grant_oh),.grant_idx(grant_idx));
integer fd,n,expected,cycle=0;
reg [1023:0] fname;
reg [7:0] expected_oh;
initial begin
  if (!$value$plusargs("VECTORS=%s",fname)) $fatal(1,"missing VECTORS");
  fd=$fopen(fname,"r");
  if (!fd) $fatal(1,"cannot open vectors");
  while (!$feof(fd)) begin
    n=$fscanf(fd,"%h %h %h %d\n",valid,remaining,age,expected);
    if (n==4) begin
      expected_oh=(expected<0) ? 8'b0 : (8'b1 << expected);
      #1;
      if (grant_valid !== (expected>=0) || grant_oh !== expected_oh ||
          (expected>=0 && grant_idx !== expected[2:0])) begin
        $display("FAIL policy=%0d cycle=%0d got=%b %h %d expected=%0d",
          POLICY,cycle,grant_valid,grant_oh,grant_idx,expected);
        $fatal(1,"selector mismatch");
      end
      cycle=cycle+1;
    end else if (n!=-1) $fatal(1,"malformed vector");
  end
  $fclose(fd);
  if (cycle!=4096) $fatal(1,"wrong count");
  $display("PASS policy=%0d vectors=%0d",POLICY,cycle);
  $finish;
end
endmodule
