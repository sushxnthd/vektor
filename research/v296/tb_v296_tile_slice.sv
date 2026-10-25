`timescale 1ns/1ps
// Independent matched RF-slice equivalence and bank-port accounting.
// All 32 RF words are initialized before issuing any wave.
module tb_v296_tile_slice;
  reg clk=0,rst_n=0;
  reg [31:0] wave_valid=0,wave_ready=0;
  reg [127:0] src0_bank_by_wave=0,src1_bank_by_wave=0;
  reg rf_write_en=0,rf_write_word=0;
  reg [3:0] rf_write_bank=0;
  reg [7:0] rf_write_data=0;
  wire [3:0] vp,vc;
  wire [4:0] p0,p1,p2,p3,c0,c1,c2,c3;
  wire [31:0] dp,dc;
  wire [4:0] wid [0:3];
  assign wid[0]=p0;
  assign wid[1]=p1;
  assign wid[2]=p2;
  assign wid[3]=p3;
  integer cycles, checked, admitted;
  integer ports [0:15];
  integer k,j,bank_a,bank_b;
  // Independent direct-index RF oracle, deliberately without shared-port muxes.
  reg [7:0] reference_rf [0:31];
  reg [31:0] expected_exec=0;
  function [7:0] oracle_read;
    input [127:0] table;
    input [4:0] id;
    reg [3:0] bank;
    begin
      bank=table[id*4 +:4];
      oracle_read=reference_rf[2*bank+id[0]];
    end
  endfunction
  always @(posedge clk)
    if(rf_write_en)
      reference_rf[{rf_write_bank,rf_write_word}] <= rf_write_data;
  integer z;
  always @(posedge clk or negedge rst_n) begin
    if(!rst_n) expected_exec<=0;
    else for(z=0;z<4;z=z+1)
      if(vp[z])
        expected_exec[8*z +:8] <=
          oracle_read(src0_bank_by_wave,wid[z]) +
          (oracle_read(src1_bank_by_wave,wid[z]) ^ {3'b000,wid[z]});
  end
  always #5 clk=~clk;

  v296_tile_slice #(.PAIRWISE(1)) pairwise(
    .clk(clk),.rst_n(rst_n),.wave_valid(wave_valid),.wave_ready(wave_ready),
    .src0_bank_by_wave(src0_bank_by_wave),.src1_bank_by_wave(src1_bank_by_wave),
    .rf_write_en(rf_write_en),.rf_write_bank(rf_write_bank),
    .rf_write_word(rf_write_word),.rf_write_data(rf_write_data),
    .issue_valid(vp),.issue_wave0(p0),.issue_wave1(p1),
    .issue_wave2(p2),.issue_wave3(p3),.executed_data(dp));
  v296_tile_slice #(.PAIRWISE(0)) serial(
    .clk(clk),.rst_n(rst_n),.wave_valid(wave_valid),.wave_ready(wave_ready),
    .src0_bank_by_wave(src0_bank_by_wave),.src1_bank_by_wave(src1_bank_by_wave),
    .rf_write_en(rf_write_en),.rf_write_bank(rf_write_bank),
    .rf_write_word(rf_write_word),.rf_write_data(rf_write_data),
    .issue_valid(vc),.issue_wave0(c0),.issue_wave1(c1),
    .issue_wave2(c2),.issue_wave3(c3),.executed_data(dc));

  task check;
  begin
    if ({vp,p0,p1,p2,p3,dp} !== {vc,c0,c1,c2,c3,dc})
      $fatal(1,"INTEGRATED_EQUIVALENCE_FAIL cycle=%0d",cycles);
    if (^dp === 1'bx || ^dc === 1'bx)
      $fatal(1,"UNINITIALIZED_EXECUTION_DATA cycle=%0d",cycles);
    if(dp !== expected_exec)
      $fatal(1,"INDEPENDENT_RF_EXECUTION_ORACLE_FAIL cycle=%0d observed=%h expected=%h",cycles,dp,expected_exec);
    for(k=0;k<16;k=k+1) ports[k]=0;
    for(k=0;k<4;k=k+1) if(vp[k]) begin
      if (!wave_valid[wid[k]] || !wave_ready[wid[k]])
        $fatal(1,"PHANTOM_ISSUE cycle=%0d slot=%0d wave=%0d",cycles,k,wid[k]);
      bank_a=src0_bank_by_wave[wid[k]*4 +:4];
      bank_b=src1_bank_by_wave[wid[k]*4 +:4];
      ports[bank_a]=ports[bank_a]+1;
      ports[bank_b]=ports[bank_b]+1;
    end
    for(j=0;j<16;j=j+1)
      if(ports[j]>2) $fatal(1,"BANK_PORT_OVERUSE cycle=%0d bank=%0d count=%0d",cycles,j,ports[j]);
    checked=checked+1;
  end
  endtask

  initial begin
    cycles=0;checked=0;admitted=0;
    repeat(3) @(negedge clk);
    rst_n=1;
    // Every bank/word pair gets an independently varying initialized value.
    for(integer b=0;b<16;b=b+1) begin
      for(integer w=0;w<2;w=w+1) begin
        @(negedge clk);
        rf_write_en=1;rf_write_bank=b;rf_write_word=w;
        rf_write_data=(b*17+w*53+9);
      end
    end
    @(negedge clk);rf_write_en=0;
    for(cycles=0;cycles<2048;cycles=cycles+1) begin
      @(negedge clk);
      wave_valid=(cycles%13==0)?32'hffffffff:$random;
      wave_ready=(cycles%13==0)?32'hffffffff:
                 (cycles%13==1)?32'h01010101:$random;
      for(integer a=0;a<4;a=a+1) begin
        src0_bank_by_wave[a*32 +:32]=$random;
        src1_bank_by_wave[a*32 +:32]=$random;
      end
      if(cycles%7==0) begin
        src0_bank_by_wave=0;src1_bank_by_wave=0;
      end
      if(cycles%7==1) src1_bank_by_wave=src0_bank_by_wave;
      if(cycles%7==2) src1_bank_by_wave=~src0_bank_by_wave;
      rf_write_en=(cycles%3==0);
      rf_write_bank=$random;rf_write_word=$random;rf_write_data=$random;
      #1;check();
      @(posedge clk);
      #1;check();
      admitted=admitted+vp[0]+vp[1]+vp[2]+vp[3];
    end
    if(checked!=4096) $fatal(1,"MISSING_EQUIVALENCE_CHECKS");
    if(admitted<100) $fatal(1,"DEGENERATE_NO_WORKLOAD");
    $display("V296_TILE_SLICE_RTL_PASS checks=%0d cycles=%0d accepted=%0d",checked,cycles,admitted);
    $finish;
  end
endmodule
