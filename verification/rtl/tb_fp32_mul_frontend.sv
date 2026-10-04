module tb_fp32_mul_frontend;
logic [31:0] a,b; logic special,sign; logic signed [10:0] exp2; logic [47:0] product;
fp32_mul_frontend dut(.*);
task check(input [31:0] x,y,input sp,sg,input signed [10:0] e,input [47:0] p); begin a=x;b=y;#1;if({special,sign,exp2,product}!={sp,sg,e,p}) $fatal(1,"mismatch"); end endtask
initial begin check(32'h3f800000,32'h40000000,0,0,-11'sd46,48'h400000000000); check(32'hbf800000,32'h3f800000,0,1,-11'sd46,48'h400000000000); check(32'h00000001,32'h3f800000,0,0,-11'sd172,48'h000000800000); $display("PASS"); $finish; end
endmodule
