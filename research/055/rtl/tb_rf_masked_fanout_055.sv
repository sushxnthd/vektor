`timescale 1ns/1ps
module tb_rf_masked_fanout_055;
  parameter integer DEDUP=1;
  reg clk=0, rst_n=0;
  reg issue_valid=0, req_ready=0, resp_valid=0, complete_ready=0;
  reg [7:0] issue_tag=0,resp_tag=0,resp_reg=0;
  reg [23:0] issue_regs=0;
  reg [2:0] issue_mask=0;
  reg [1:0] resp_operand=0;
  reg [31:0] resp_data=0;
  wire issue_ready,req_valid,complete_valid,resp_error;
  wire [7:0] req_tag,req_reg,complete_tag;
  wire [1:0] req_operand;
  wire [95:0] complete_data;
  rf_masked_fanout_055 #(.DEDUP(DEDUP)) dut(
    .clk(clk),.rst_n(rst_n),.issue_valid(issue_valid),.issue_ready(issue_ready),
    .issue_tag(issue_tag),.issue_regs(issue_regs),.issue_mask(issue_mask),.req_valid(req_valid),
    .req_ready(req_ready),.req_tag(req_tag),.req_operand(req_operand),.req_reg(req_reg),
    .resp_valid(resp_valid),.resp_tag(resp_tag),.resp_operand(resp_operand),
    .resp_reg(resp_reg),.resp_data(resp_data),.complete_valid(complete_valid),
    .complete_ready(complete_ready),.complete_tag(complete_tag),
    .complete_data(complete_data),.resp_error(resp_error)
  );
  integer fd,n,cycle=0,rc;
  reg [1023:0] fname;
  integer vi,rr,rv,ro,cr,er,eq,ec,im;
  reg [7:0] it,rt,rg,eqt,eqg,ect;
  reg [23:0] ir;
  reg [1:0] op,eop;
  reg [31:0] rd;
  reg [95:0] ecd;
  initial begin
    if (!$value$plusargs("VECTORS=%s",fname)) $fatal(1,"missing VECTORS");
    fd=$fopen(fname,"r");
    if (!fd) $fatal(1,"cannot open vectors");
    #2;clk=1;#2;clk=0;rst_n=1;
    while (!$feof(fd)) begin
      n=$fscanf(fd,"%d %d %h %h %h %d %d %h %d %h %h %d %d %d %h %d %h %d %h %h %d\n",
        rc,vi,it,ir,im,rr,rv,rt,op,rg,rd,cr,er,eq,eqt,eop,eqg,ec,ect,ecd,ro);
      if (n==21) begin
        issue_valid=vi;issue_tag=it;issue_regs=ir;issue_mask=im;req_ready=rr;
        resp_valid=rv;resp_tag=rt;resp_operand=op;resp_reg=rg;
        resp_data=rd;complete_ready=cr;
        #1;
        if (issue_ready !== er[0] || req_valid !== eq[0] ||
            (req_valid && (req_tag!==eqt || req_operand!==eop || req_reg!==eqg)) ||
            complete_valid !== ec[0] ||
            (complete_valid && (complete_tag!==ect || complete_data!==ecd)) ||
            resp_error !== ro[0]) begin
          $display("FAIL cycle=%0d dedup=%0d",cycle,DEDUP);
          $display("issue_ready %b expected %b req_valid %b expected %b",issue_ready,er[0],req_valid,eq[0]);
          $display("req tag/op/reg %h %d %h expected %h %d %h",req_tag,req_operand,req_reg,eqt,eop,eqg);
          $display("complete %b tag %h data %h expected %b %h %h",complete_valid,complete_tag,complete_data,ec[0],ect,ecd);
          $display("resp_error %b expected %b",resp_error,ro[0]);
          $fatal(1,"differential mismatch");
        end
        clk=1;#1;clk=0;#1;cycle=cycle+1;
      end else if (n!=-1) $fatal(1,"malformed vector row at %0d parsed=%0d",cycle,n);
    end
    $fclose(fd);
    $display("PASS Vektor-055 RTL differential: %0d cycles DEDUP=%0d",cycle,DEDUP);
    $finish;
  end
endmodule
