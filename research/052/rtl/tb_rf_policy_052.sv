`timescale 1ns/1ps
module tb_rf_policy_052;
  parameter W=4, B=2, O=3, PORTS=2, POLICY=2;
  localparam BW=(B<2 ? 1 : $clog2(B));
  localparam WW=(W<2 ? 1 : $clog2(W));
  localparam SW=(W*O<2 ? 1 : $clog2(W*O+1));
  reg clk=0, rst_n=0;
  reg [W*O-1:0] pending_mask=0, accepted_mask=0;
  reg [W*O*BW-1:0] bank_ids=0;
  reg [SW-1:0] free_slots=0;
  wire [W*O-1:0] grant;
  wire [SW-1:0] grant_count;
  wire [WW-1:0] pointer;
  reg [W*O-1:0] exp_grant;
  reg [SW-1:0] exp_count;
  reg [WW-1:0] exp_pointer;
  reg [1023:0] vector_path;
  integer fd, r, step=0;
  rf_policy_052 #(.W(W),.B(B),.O(O),.PORTS(PORTS),.POLICY(POLICY)) dut(
    .clk(clk),.rst_n(rst_n),.pending_mask(pending_mask),
    .accepted_mask(accepted_mask),.bank_ids(bank_ids),.free_slots(free_slots),
    .grant(grant),.grant_count(grant_count),.pointer(pointer));
  initial begin
    if (!$value$plusargs("VECTORS=%s", vector_path))
      $fatal(1,"missing +VECTORS=file");
    fd=$fopen(vector_path,"r");
    if (!fd) $fatal(1,"cannot open vector file");
    #2; rst_n=1;
    while (!$feof(fd)) begin
      r=$fscanf(fd,"%h %h %h %h %h %h %h\n",
        pending_mask,accepted_mask,bank_ids,free_slots,
        exp_grant,exp_count,exp_pointer);
      if (r != 7) begin
        if (!$feof(fd)) $fatal(1,"malformed vector at %0d, got %0d fields",step,r);
      end else begin
        #1;
        if (grant !== exp_grant || grant_count !== exp_count)
          $fatal(1,"grant mismatch step=%0d got=%h/%h want=%h/%h ptr=%0d",
                 step,grant,grant_count,exp_grant,exp_count,pointer);
        clk=1;
        #1;
        if (pointer !== exp_pointer)
          $fatal(1,"pointer mismatch step=%0d got=%0d want=%0d",step,pointer,exp_pointer);
        clk=0;
        #1;
        step=step+1;
      end
    end
    $fclose(fd);
    if (step<100) $fatal(1,"insufficient vectors %0d",step);
    $display("PASS W=%0d B=%0d POLICY=%0d steps=%0d",W,B,POLICY,step);
    $finish;
  end
endmodule
