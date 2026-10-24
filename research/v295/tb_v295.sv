`timescale 1ns/1ps
module tb_v295;
 reg clk=0,rst_n=0;
 reg [31:0] wave_valid=0,wave_ready=0;
 reg [127:0] src0_bank_by_wave=0,src1_bank_by_wave=0;
 wire [3:0] vr,vc,vp;
 wire [4:0] r0,r1,r2,r3,c0,c1,c2,c3,p0,p1,p2,p3;
 integer i,k;
 always #5 clk=~clk;
 vektor_issue_control ref_dut(
  .clk(clk),.rst_n(rst_n),.wave_valid(wave_valid),.wave_ready(wave_ready),
  .src0_bank_by_wave(src0_bank_by_wave),.src1_bank_by_wave(src1_bank_by_wave),
  .issue_valid(vr),.issue_wave0(r0),.issue_wave1(r1),
  .issue_wave2(r2),.issue_wave3(r3));
 v295_issue_core #(.PREDECODE(0)) ctrl(
  .clk(clk),.rst_n(rst_n),.wave_valid(wave_valid),.wave_ready(wave_ready),
  .src0_bank_by_wave(src0_bank_by_wave),.src1_bank_by_wave(src1_bank_by_wave),
  .issue_valid(vc),.issue_wave0(c0),.issue_wave1(c1),
  .issue_wave2(c2),.issue_wave3(c3));
 v295_issue_core #(.PREDECODE(1)) candidate(
  .clk(clk),.rst_n(rst_n),.wave_valid(wave_valid),.wave_ready(wave_ready),
  .src0_bank_by_wave(src0_bank_by_wave),.src1_bank_by_wave(src1_bank_by_wave),
  .issue_valid(vp),.issue_wave0(p0),.issue_wave1(p1),
  .issue_wave2(p2),.issue_wave3(p3));
 task check;
 begin
  if({vr,r0,r1,r2,r3} !== {vc,c0,c1,c2,c3})
   $fatal(1,"V295 optimized control mismatch at %0d",i);
  if({vr,r0,r1,r2,r3} !== {vp,p0,p1,p2,p3})
   $fatal(1,"V295 predecode mismatch at %0d",i);
 end
 endtask
 initial begin
  repeat(3) @(negedge clk);
  rst_n=1;
  for(i=0;i<2048;i=i+1) begin
   @(negedge clk);
   wave_valid=$random;
   wave_ready=(i%4==0)?32'hffffffff:
              (i%4==1)?32'h01010101:$random;
   for(k=0;k<4;k=k+1) begin
    src0_bank_by_wave[k*32 +: 32]=$random;
    src1_bank_by_wave[k*32 +: 32]=$random;
   end
   if(i%8==0) begin src0_bank_by_wave=0;src1_bank_by_wave=0;end
   if(i%8==1) src1_bank_by_wave=src0_bank_by_wave;
   #1;check();
   @(posedge clk);
   #1;check();
  end
  $display("V295 PASS 2048 randomized cycles, 3-way pre/post-clock comparison");
  $finish;
 end
endmodule
