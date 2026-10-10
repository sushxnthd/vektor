module tb_wb_return_debt_096;
reg clk=0;
always #5 clk=~clk;
initial begin
#100;
$finish;
end
endmodule
