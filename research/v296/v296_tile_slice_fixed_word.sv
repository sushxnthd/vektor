// Preregistered: FIXED_WORD_TWO_PORT_RF_CONE_PREREG_20261027.md
// Symmetric fixed-word two-port RF proxy falsification; no GPU claim.
// Original matched slice remains unchanged. This is NOT a new mechanism.
// V296 prospective balanced RF-return crossbar implementation trial, NOT a full GPU.
// One physical two-read-port-per-bank RF fabric shared by both arbiter variants.
// See TILE_SLICE_PHYSICAL_PREREG_20261025.md. Do not change resource counts.
module v296_tile_slice_fixed_word #(parameter integer PAIRWISE = 1)(
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

  // Speculative one-hot bank-index decode, identical for both arbiters.
  // All 32 nibbles are decoded in parallel, then reduced by a balanced OR tree.
  // This replaces only the variable shift; no RF ports or pipeline state change.
  function automatic [3:0] lookup_bank;
    input [127:0] bank_map;
    input [4:0] id;
    reg [3:0] leaf [0:31];
    reg [3:0] level16 [0:15];
    reg [3:0] level8 [0:7];
    reg [3:0] level4 [0:3];
    reg [3:0] level2 [0:1];
    integer t;
    begin
      for (t=0; t<32; t=t+1)
        leaf[t] = bank_map[4*t +: 4] & {4{(id == t)}};
      for (t=0; t<16; t=t+1)
        level16[t] = leaf[2*t] | leaf[2*t+1];
      for (t=0; t<8; t=t+1)
        level8[t] = level16[2*t] | level16[2*t+1];
      for (t=0; t<4; t=t+1)
        level4[t] = level8[2*t] | level8[2*t+1];
      for (t=0; t<2; t=t+1)
        level2[t] = level4[2*t] | level4[2*t+1];
      lookup_bank = level2[0] | level2[1];
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

   // TWO fixed physical read ports per two-word bank: port 0 reads word 0,
  // port 1 reads word 1. Both outputs may broadcast to multiple consumers.
  // This is equivalent only for the deliberately shallow 2-word RF proxy.
  // It does NOT generalize to realistic deep SRAM banks.
  // No third read port, new RF word, or new issue slot is instantiated.
  wire [7:0] operand_data [0:7];
  genvar ox, ob;
  generate for(ox=0;ox<8;ox=ox+1) begin: fixed_word_return
    wire [7:0] masked [0:15];
    wire [7:0] stage8 [0:7];
    wire [7:0] stage4 [0:3];
    wire [7:0] stage2 [0:1];
    for(ob=0;ob<16;ob=ob+1) begin: bank
      wire hit;
      wire [7:0] fixed_word0;
      wire [7:0] fixed_word1;
      wire [7:0] selected_word;
      assign hit = op_valid[ox] && (op_bank[ox] == ob);
      assign fixed_word0 = rf[2*ob];
      assign fixed_word1 = rf[2*ob+1];
      assign selected_word = op_word[ox] ? fixed_word1 : fixed_word0;
      assign masked[ob] = {8{hit}} & selected_word;
    end
    for(ob=0;ob<8;ob=ob+1) begin: level8
      assign stage8[ob] = masked[2*ob] | masked[2*ob+1];
    end
    for(ob=0;ob<4;ob=ob+1) begin: level4
      assign stage4[ob] = stage8[2*ob] | stage8[2*ob+1];
    end
    for(ob=0;ob<2;ob=ob+1) begin: level2
      assign stage2[ob] = stage4[2*ob] | stage4[2*ob+1];
    end
    assign operand_data[ox] = stage2[0] | stage2[1];
  end endgenerate

 // Symmetric operand-capture boundary. RF values are sampled BEFORE
  // same-edge RF writes, preserving the original read-before-write behavior.
  // The execute result becomes visible exactly one edge later; no extra
  // read port or wave issue slot is added. Both PAIRWISE values use this.
  reg [7:0] staged_operand_data [0:7];
  reg [4:0] staged_wave_id [0:3];
  reg [3:0] staged_valid;
  integer q;
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      executed_data <= 0;
      staged_valid <= 0;
      for (q=0; q<4; q=q+1) begin
        staged_wave_id[q] <= 0;
        staged_operand_data[2*q] <= 0;
        staged_operand_data[2*q+1] <= 0;
      end
    end else begin
      for (q=0; q<4; q=q+1) begin
        staged_valid[q] <= issue_valid[q];
        // Capture data only for admitted waves; old values are ignored
        // when staged_valid is low.
        if (issue_valid[q]) begin
          staged_wave_id[q] <= wave_id[q];
          staged_operand_data[2*q] <= operand_data[2*q];
          staged_operand_data[2*q+1] <= operand_data[2*q+1];
        end
        if (staged_valid[q])
          executed_data[8*q +:8] <=
            staged_operand_data[2*q] +
            (staged_operand_data[2*q+1] ^ {3'b000,staged_wave_id[q]});
      end
    end
  end
endmodule
