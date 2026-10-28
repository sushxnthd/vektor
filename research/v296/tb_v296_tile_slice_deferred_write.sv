`timescale 1ns/1ps
// Independent deep-bank direct-index oracle. Two dynamic read ports per bank.
// Frozen by DEEP_BANK_DYNAMIC_TWO_PORT_PREREG_20261027.md.
// WORD_BITS=2,3,4; tests 4,8,16 words/bank without fixed-word shortcuts.
module tb_v296_tile_slice_deferred_write;
  parameter integer WORD_BITS = 3;
  localparam integer DEPTH = (1 << WORD_BITS);
  reg clk=0, rst_n=0;
  reg [31:0] wave_valid=0, wave_ready=0;
  reg [127:0] src0_bank_by_wave=0, src1_bank_by_wave=0;
  reg rf_write_en=0;
  reg [3:0] rf_write_bank=0;
  reg [WORD_BITS-1:0] rf_write_word=0;
  reg [7:0] rf_write_data=0;
  wire [3:0] vp, vs;
  wire [4:0] p0,p1,p2,p3,s0,s1,s2,s3;
  wire [31:0] dp,ds;
  wire [4:0] wid [0:3];
  assign wid[0]=p0;
  assign wid[1]=p1;
  assign wid[2]=p2;
  assign wid[3]=p3;
  v296_tile_slice_deferred_write #(.PAIRWISE(1),.WORD_BITS(WORD_BITS)) candidate(
    .clk(clk),.rst_n(rst_n),.wave_valid(wave_valid),.wave_ready(wave_ready),
    .src0_bank_by_wave(src0_bank_by_wave),.src1_bank_by_wave(src1_bank_by_wave),
    .rf_write_en(rf_write_en),.rf_write_bank(rf_write_bank),
    .rf_write_word(rf_write_word),.rf_write_data(rf_write_data),
    .issue_valid(vp),.issue_wave0(p0),.issue_wave1(p1),
    .issue_wave2(p2),.issue_wave3(p3),.executed_data(dp));
  v296_tile_slice_deferred_write #(.PAIRWISE(0),.WORD_BITS(WORD_BITS)) serial(
    .clk(clk),.rst_n(rst_n),.wave_valid(wave_valid),.wave_ready(wave_ready),
    .src0_bank_by_wave(src0_bank_by_wave),.src1_bank_by_wave(src1_bank_by_wave),
    .rf_write_en(rf_write_en),.rf_write_bank(rf_write_bank),
    .rf_write_word(rf_write_word),.rf_write_data(rf_write_data),
    .issue_valid(vs),.issue_wave0(s0),.issue_wave1(s1),
    .issue_wave2(s2),.issue_wave3(s3),.executed_data(ds));

  reg [7:0] independent_rf [0:16*DEPTH-1];
  reg [7:0] oracle_pre_data [0:7];
  reg [4:0] oracle_pre_wave [0:3];
  reg [3:0] oracle_pre_valid=0;
  reg [7:0] oracle_staged [0:7];
  reg [4:0] oracle_wave [0:3];
  reg [3:0] oracle_valid=0;
  reg [31:0] oracle_exec=0;
  integer z;
  function [7:0] direct_read;
    input [127:0] bank_map;
    input [4:0] id;
    reg [3:0] bank;
    begin
      bank=bank_map[id*4 +: 4];
      direct_read=independent_rf[bank*DEPTH+id[WORD_BITS-1:0]];
    end
  endfunction
  // Reference uses no port assignment, mux-tree, or internal DUT state.
  always @(posedge clk)
    if(rf_write_en)
      independent_rf[{rf_write_bank,rf_write_word}] <= rf_write_data;
  always @(posedge clk or negedge rst_n) begin
    if(!rst_n) begin
      oracle_pre_valid<=0;
      oracle_valid<=0;
      oracle_exec<=0;
      for(z=0;z<4;z=z+1) begin
        oracle_wave[z]<=0;
        oracle_pre_wave[z]<=0;
        oracle_pre_data[2*z]<=0;
        oracle_pre_data[2*z+1]<=0;
        oracle_staged[2*z]<=0;
        oracle_staged[2*z+1]<=0;
      end
    end else begin
      for(z=0;z<4;z=z+1) begin
        oracle_pre_valid[z]<=vp[z];
        if(vp[z]) begin
          oracle_pre_wave[z]<=wid[z];
          oracle_pre_data[2*z]<=direct_read(src0_bank_by_wave,wid[z]);
          oracle_pre_data[2*z+1]<=direct_read(src1_bank_by_wave,wid[z]);
        end
        oracle_valid[z]<=oracle_pre_valid[z];
        if(oracle_pre_valid[z]) begin
          oracle_wave[z]<=oracle_pre_wave[z];
          oracle_staged[2*z]<=oracle_pre_data[2*z];
          oracle_staged[2*z+1]<=oracle_pre_data[2*z+1];
        end
        if(oracle_valid[z])
          oracle_exec[8*z +:8] <=
            oracle_staged[2*z]+
            (oracle_staged[2*z+1] ^ {3'b000,oracle_wave[z]});
      end
    end
  end
  always #5 clk=~clk;
  integer cycle, b,w,k,j,accepted=0,checked=0,reads,collisions=0;
  integer bank_ports [0:15];
  reg [DEPTH-1:0] word_seen=0;
  task check_issue;
  begin
    if ({vp,p0,p1,p2,p3} !== {vs,s0,s1,s2,s3})
      $fatal(1,"DEEP_BANK_ISSUE_MISMATCH depth=%0d cycle=%0d",DEPTH,cycle);
    for(k=0;k<16;k=k+1) bank_ports[k]=0;
    for(k=0;k<4;k=k+1) if(vp[k]) begin
      if(!wave_valid[wid[k]] || !wave_ready[wid[k]])
        $fatal(1,"DEEP_BANK_PHANTOM_ISSUE depth=%0d cycle=%0d",DEPTH,cycle);
      bank_ports[src0_bank_by_wave[wid[k]*4 +:4]]++;
      bank_ports[src1_bank_by_wave[wid[k]*4 +:4]]++;
      word_seen[wid[k][WORD_BITS-1:0]]=1'b1;
      accepted++;
    end
    for(j=0;j<16;j=j+1)
      if(bank_ports[j]>2)
        $fatal(1,"DEEP_BANK_THIRD_READ depth=%0d cycle=%0d bank=%0d",DEPTH,cycle,j);
    checked++;
  end
  endtask
  initial begin
    if(WORD_BITS<2 || WORD_BITS>4)
      $fatal(1,"UNSUPPORTED_TEST_WORD_BITS");
    repeat(3) @(negedge clk);
    rst_n=1;
    // Initialize every word independently while no waves are issuable.
    for(b=0;b<16;b=b+1)
      for(w=0;w<DEPTH;w=w+1) begin
        @(negedge clk);
        rf_write_en=1;rf_write_bank=b;rf_write_word=w;
        rf_write_data=b*17+w*53+9;
      end
    @(negedge clk);rf_write_en=0;
    repeat(2) @(negedge clk); // Drain the final deferred initialization write.
    for(cycle=0;cycle<2048;cycle=cycle+1) begin
      @(negedge clk);
      wave_valid=(cycle%13==0)?32'hffffffff:$random;
      wave_ready=(cycle%13==0)?32'hffffffff:
                 (cycle%13==1)?32'h01010101:$random;
      for(integer a=0;a<4;a=a+1) begin
        src0_bank_by_wave[a*32 +:32]=$random;
        src1_bank_by_wave[a*32 +:32]=$random;
      end
      if(cycle%7==0) begin
        src0_bank_by_wave=0;src1_bank_by_wave=0;
      end
      if(cycle%7==1) src1_bank_by_wave=src0_bank_by_wave;
      if(cycle%7==2) src1_bank_by_wave=~src0_bank_by_wave;
      rf_write_en=(cycle%3==0);
      rf_write_bank=$random;rf_write_word=$random;rf_write_data=$random;
      #1;
      // Force frequent same-edge RF read/write collisions, including
      // repeated writes to the same word. No change to issue arbitration.
      if (cycle%11==0 && vp[0]) begin
        rf_write_en=1;
        rf_write_bank=src0_bank_by_wave[p0*4 +:4];
        rf_write_word=p0[WORD_BITS-1:0];
      end
      for(integer ci=0;ci<4;ci=ci+1) if(vp[ci] && rf_write_en) begin
        if ((rf_write_bank==src0_bank_by_wave[wid[ci]*4 +:4] ||
             rf_write_bank==src1_bank_by_wave[wid[ci]*4 +:4]) &&
             rf_write_word==wid[ci][WORD_BITS-1:0])
          collisions++;
      end
      check_issue();
      @(posedge clk);
      #1;
      if(dp !== ds || dp !== oracle_exec)
        $fatal(1,"DEEP_BANK_ORACLE_MISMATCH depth=%0d cycle=%0d pair=%h serial=%h oracle=%h",
               DEPTH,cycle,dp,ds,oracle_exec);
      if(^dp === 1'bx)
        $fatal(1,"DEEP_BANK_X_DATA depth=%0d cycle=%0d",DEPTH,cycle);
    end
    if(collisions<20) $fatal(1,"INSUFFICIENT_WRITE_COLLISIONS depth=%0d count=%0d",DEPTH,collisions);
    if(checked!=2048 || accepted<100)
      $fatal(1,"DEEP_BANK_INSUFFICIENT_STRESS depth=%0d accepted=%0d",DEPTH,accepted);
    reads=0;
    for(j=0;j<DEPTH;j=j+1) reads=reads+word_seen[j];
    if(reads<DEPTH/2)
      $fatal(1,"DEEP_BANK_INSUFFICIENT_ADDRESS_COVERAGE depth=%0d words=%0d",DEPTH,reads);
    $display("V296_DEFERRED_WRITE_RTL_PASS depth=%0d cycles=%0d accepted=%0d word_addresses=%0d collisions=%0d",
             DEPTH,checked,accepted,reads,collisions);
    $finish;
  end
endmodule
