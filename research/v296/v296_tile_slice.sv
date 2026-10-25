// V296 matched banked-RF execution slice. Exploratory integration, NOT a full GPU.
// One physical two-read-port-per-bank RF fabric shared by both arbiter variants.
// See TILE_SLICE_PHYSICAL_PREREG_20261025.md. Do not change resource counts.
module v296_tile_slice #(parameter integer PAIRWISE = 1)(
  input wire clk, rst_n,
  input wire [31:0] wave_valid, wave_ready,
  input wire [127:0] src0_bank_by_wave, src1_bank_by_wave,
  input wire rf_write_en,
  input wire [3:0] rf_write_bank,
  input wire rf_write_word,
  input wire [7:0] rf_write_data,
  output wire [3:0] issue_valid,
  output wire [4:0] issue_wave0, issue_wave1, issue_wave2, issue_wave3,
  output reg [31:0] executed_data
);
  generate if (PAIRWISE) begin: candidate
    v296_issue_core issue(
      .clk(clk),.rst_n(rst_n),.wave_valid(wave_valid),.wave_ready(wave_ready),
      .src0_bank_by_wave(src0_bank_by_wave),.src1_bank_by_wave(src1_bank_by_wave),
      .issue_valid(issue_valid),.issue_wave0(issue_wave0),
      .issue_wave1(issue_wave1),.issue_wave2(issue_wave2),.issue_wave3(issue_wave3));
  end else begin: strongest_serial
    v295_issue_core #(.PREDECODE(0)) issue(
      .clk(clk),.rst_n(rst_n),.wave_valid(wave_valid),.wave_ready(wave_ready),
      .src0_bank_by_wave(src0_bank_by_wave),.src1_bank_by_wave(src1_bank_by_wave),
      .issue_valid(issue_valid),.issue_wave0(issue_wave0),
      .issue_wave1(issue_wave1),.issue_wave2(issue_wave2),.issue_wave3(issue_wave3));
  end endgenerate

  wire [4:0] wave_id [0:3];
  assign wave_id[0] = issue_wave0;
  assign wave_id[1] = issue_wave1;
  assign wave_id[2] = issue_wave2;
  assign wave_id[3] = issue_wave3;

  function [3:0] lookup_bank;
    input [127:0] bank_map;
    input [4:0] id;
    reg [127:0] shifted;
    begin
      shifted = bank_map >> (id*4);
      lookup_bank = shifted[3:0];
    end
  endfunction

  // Eight logical operands from four accepted waves, distributed across
  // 16 banks with a HARD maximum of two read ports per bank.
  wire [3:0] op_bank [0:7];
  wire op_valid [0:7];
  wire op_word [0:7];
  genvar s;
  generate for (s=0;s<4;s=s+1) begin: operand_map
    assign op_bank[2*s] = lookup_bank(src0_bank_by_wave,wave_id[s]);
    assign op_bank[2*s+1] = lookup_bank(src1_bank_by_wave,wave_id[s]);
    assign op_valid[2*s] = issue_valid[s];
    assign op_valid[2*s+1] = issue_valid[s];
    assign op_word[2*s] = wave_id[s][0];
    assign op_word[2*s+1] = wave_id[s][0];
  end endgenerate

  // 16 banks x 2 words x 8 bits, with one GLOBAL write port.
  // This is a flop RF proxy, NOT an SRAM macro or production GPU RF.
  reg [7:0] rf [0:31];
  always @(posedge clk) begin
    if (rf_write_en)
      rf[{rf_write_bank,rf_write_word}] <= rf_write_data;
  end

  wire [7:0] bank_data0 [0:15];
  wire [7:0] bank_data1 [0:15];
  genvar b;
  generate for (b=0;b<16;b=b+1) begin: bank_two_ports
    reg have0,have1;
    reg addr0,addr1;
    integer k;
    always @* begin
      have0=0;have1=0;addr0=0;addr1=0;
      for(k=0;k<8;k=k+1) begin
        if(op_valid[k] && op_bank[k]==b) begin
          if(!have0) begin
            have0=1;
            addr0=op_word[k];
          end else if(!have1) begin
            have1=1;
            addr1=op_word[k];
          end
        end
      end
    end
    assign bank_data0[b] = rf[2*b+addr0];
    assign bank_data1[b] = rf[2*b+addr1];
  end endgenerate

  // Each admitted operand selects port 0 or port 1 by its deterministic
  // rank among earlier admitted operands accessing the same bank.
  reg [7:0] use_second;
  integer i,j;
  always @* begin
    use_second=0;
    for(i=0;i<8;i=i+1)
      for(j=0;j<8;j=j+1)
        if(j<i && op_valid[i] && op_valid[j] && op_bank[i]==op_bank[j])
          use_second[i]=1'b1;
  end
  reg [7:0] operand_data [0:7];
  integer x,y;
  always @* begin
    for(x=0;x<8;x=x+1) begin
      operand_data[x]=0;
      for(y=0;y<16;y=y+1)
        if(op_valid[x] && op_bank[x]==y)
          operand_data[x]=use_second[x]?bank_data1[y]:bank_data0[y];
    end
  end

  // A deliberately small, nontrivial downstream execute register boundary.
  // Both contestants see identical RF and execution logic and output loads.
  integer q;
  always @(posedge clk or negedge rst_n) begin
    if(!rst_n) executed_data<=0;
    else for(q=0;q<4;q=q+1)
      if(issue_valid[q])
        executed_data[8*q +:8] <=
          operand_data[2*q] + (operand_data[2*q+1] ^ {3'b000,wave_id[q]});
  end
endmodule
