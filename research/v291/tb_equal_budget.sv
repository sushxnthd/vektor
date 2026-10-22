// Falsification: multicast versus conventional equal-budget broadcast.
module tb_v291_equal_budget;
reg [3:0] valid;
reg [63:0] tag;
reg [31:0] data;
wire dut_read, ctl_read;
wire [15:0] dut_tag, ctl_tag;
wire [3:0] dut_served, ctl_served;
wire [127:0] dut_data, ctl_data;
integer v,p,i,checks;
v291_multicast #(.TAG_W(16)) dut (
  .valid(valid), .tag(tag), .rf_data(data),
  .rf_read(dut_read), .rf_tag(dut_tag),
  .served(dut_served), .consumer_data(dut_data)
);
v291_equal_budget_broadcast #(.TAG_W(16)) ctl (
  .valid(valid), .tag(tag), .rf_data(data),
  .rf_read(ctl_read), .rf_tag(ctl_tag),
  .served(ctl_served), .consumer_data(ctl_data)
);
task automatic verify;
integer j;
begin
  #1;
  if (dut_read !== ctl_read || dut_tag !== ctl_tag ||
      dut_served !== ctl_served || dut_data !== ctl_data)
    $fatal(1,"matched broadcast mismatch valid=%h tags=%h dut=%h ctl=%h",
      valid,tag,dut_served,ctl_served);
  if ((dut_served & ~valid) != 0)
    $fatal(1,"served invalid request");
  if (dut_read !== (|valid))
    $fatal(1,"RF read invariant violated");
  for(j=0;j<4;j=j+1) begin
    if(dut_served[j] && tag[j*16 +:16] !== dut_tag)
      $fatal(1,"wrong physical register delivered");
    if(dut_data[j*32 +:32] !== (dut_served[j] ? data : 32'b0))
      $fatal(1,"consumer data incorrect");
  end
  checks=checks+1;
end
endtask
initial begin
  checks=0; valid=0; tag=0; data=32'hA1B2C3D4;
  // Exhaustive 4 request-valid bits x 4^4 tag alias patterns.
  for(v=0;v<16;v=v+1)
    for(p=0;p<256;p=p+1) begin
      valid=v;
      for(i=0;i<4;i=i+1)
        tag[i*16 +:16] = (p>>(2*i)) & 3;
      verify;
    end
  // Frozen independent address/version/warp alias and collision stress.
  for(p=0;p<50000;p=p+1) begin
    valid = (p*17 + p/17) & 15;
    data = (p*32'h9e3779b9) ^ 32'hC0FFEE12;
    for(i=0;i<4;i=i+1)
      tag[i*16 +:16] = (p*37 + i*509) & 16'hffff;
    if(p%5==0) tag[31:16]=tag[15:0];
    if(p%7==0) tag[47:32]=tag[15:0];
    if(p%11==0) tag[63:48]=tag[15:0];
    if(p%13==0) tag[31:16]=tag[15:0] ^ 16'h0100;
    if(p%17==0) tag[47:32]=tag[15:0] ^ 16'h0001;
    verify;
  end
  $display("V291 EQUAL_BUDGET PASS checks=%0d mismatches=0",checks);
  $finish;
end
endmodule
