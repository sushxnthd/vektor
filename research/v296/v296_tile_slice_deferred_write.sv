// V296 implementation experiment; prereg DEFERRED_WRITE_RF_RETIMING_PREREG_20261028.md
// Ordinary running-operation semantics only; quiescent reset required.
// Preregistered: DEEP_BANK_DYNAMIC_TWO_PORT_PREREG_20261027.md
// Symmetric depth-parameterized dynamic RF transfer experiment.
// No production macro or GPU performance claim. WORD_BITS in 2..4 for hosted tests.
// Preregistered: BANK_DECODE_SHARED_ONEHOT_PREREG_20261026.md
// Experimental symmetric +1-cycle operand-capture retiming; no GPU claim.
// Original matched slice remains unchanged. This is NOT a new mechanism.
// V296 prospective balanced RF-return crossbar implementation trial, NOT a full GPU.
// One physical two-read-port-per-bank RF fabric shared by both arbiter variants.
// See TILE_SLICE_PHYSICAL_PREREG_20261025.md. Do not change resource counts.
module v296_tile_slice_deferred_write #(parameter integer PAIRWISE = 1, parameter integer WORD_BITS = 3)(
  input wire clk, rst_n,
  input wire [31:0] wave_valid, wave_ready,
  input wire [127:0] src0_bank_by_wave, src1_bank_by_wave,
  input wire rf_write_en,
  input wire [3:0] rf_write_bank,
  input wire [WORD_BITS-1:0] rf_write_word,
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
  wire [WORD_BITS-1:0] op_word [0:7];
  genvar s;
  generate for (s=0;s<4;s=s+1) begin: operand_map
    assign op_bank[2*s] = lookup_bank(src0_bank_by_wave,wave_id[s]);
    assign op_bank[2*s+1] = lookup_bank(src1_bank_by_wave,wave_id[s]);
    assign op_valid[2*s] = issue_valid[s];
    assign op_valid[2*s+1] = issue_valid[s];
    assign op_word[2*s] = wave_id[s][WORD_BITS-1:0];
    assign op_word[2*s+1] = wave_id[s][WORD_BITS-1:0];
  end endgenerate

  // At issue edge t, freeze the two-port read request. At edge t+1
  // the RF read observes the pre-W_t version because W_t is committed
  // on that same edge (nonblocking writes), exactly like the old t read.
  reg [3:0] registered_bank [0:7];
  reg [WORD_BITS-1:0] registered_word [0:7];
  reg [7:0] registered_valid;
  reg [4:0] registered_wave [0:3];
  reg [3:0] registered_issue_valid;
  integer r;
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      registered_valid <= 0;
      registered_issue_valid <= 0;
      for (r=0; r<8; r=r+1) begin
        registered_bank[r] <= 0;
        registered_word[r] <= 0;
      end
      for (r=0; r<4; r=r+1) registered_wave[r] <= 0;
    end else begin
      registered_issue_valid <= issue_valid;
      for (r=0; r<8; r=r+1) begin
        registered_bank[r] <= op_bank[r];
        registered_word[r] <= op_word[r];
        registered_valid[r] <= op_valid[r];
      end
      for (r=0; r<4; r=r+1) registered_wave[r] <= wave_id[r];
    end
  end

  // 16 banks x (2**WORD_BITS) words x 8 bits. Two dynamically
  // addressed physical read ports per bank; one GLOBAL write port.
  // Flop RF proxy only: not a GPU SRAM/register-file macro.
  localparam integer DEPTH = (1 << WORD_BITS);
  reg [7:0] rf [0:16*DEPTH-1];
  // One global write port; delay each write exactly one edge.
  // Protocol: reset only with the write pipeline drained; no RF writes
  // while reset is asserted. No third RF read or old-value snapshot.
  reg pending_write_valid;
  reg [3:0] pending_write_bank;
  reg [WORD_BITS-1:0] pending_write_word;
  reg [7:0] pending_write_data;
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      pending_write_valid <= 0;
      pending_write_bank <= 0;
      pending_write_word <= 0;
      pending_write_data <= 0;
    end else begin
      pending_write_valid <= rf_write_en;
      if (rf_write_en) begin
        pending_write_bank <= rf_write_bank;
        pending_write_word <= rf_write_word;
        pending_write_data <= rf_write_data;
      end
    end
  end
  always @(posedge clk) begin
    if (pending_write_valid)
      rf[{pending_write_bank,pending_write_word}] <= pending_write_data;
  end

  wire [7:0] bank_data0 [0:15];
  wire [7:0] bank_data1 [0:15];
  genvar b;
  generate for (b=0;b<16;b=b+1) begin: bank_two_ports
    reg have0,have1;
    reg [WORD_BITS-1:0] addr0,addr1;
    integer k;
    always @* begin
      have0=0;have1=0;addr0=0;addr1=0;
      for(k=0;k<8;k=k+1) begin
        if(registered_valid[k] && registered_bank[k]==b) begin
          if(!have0) begin
            have0=1;
            addr0=registered_word[k];
          end else if(!have1) begin
            have1=1;
            addr1=registered_word[k];
          end
        end
      end
    end
    assign bank_data0[b] = rf[b*DEPTH+addr0];
    assign bank_data1[b] = rf[b*DEPTH+addr1];
  end endgenerate

  // Each admitted operand selects port 0 or port 1 by its deterministic
  // rank among earlier admitted operands accessing the same bank.
  reg [7:0] use_second;
  integer i,j;
  always @* begin
    use_second=0;
    for(i=0;i<8;i=i+1)
      for(j=0;j<8;j=j+1)
        if(j<i && registered_valid[i] && registered_valid[j] && registered_bank[i]==registered_bank[j])
          use_second[i]=1'b1;
  end
  // One-hot bank select followed by a balanced four-level OR reduction.
  // No additional RF read ports: bank_data0/1 are still the original two
  // physical port outputs; only their RETURN crossbar is re-factored.
  wire [7:0] operand_data [0:7];
  genvar ox, ob;
  generate for(ox=0;ox<8;ox=ox+1) begin: balanced_return
    wire [7:0] masked [0:15];
    wire [7:0] stage8 [0:7];
    wire [7:0] stage4 [0:3];
    wire [7:0] stage2 [0:1];
    for(ob=0;ob<16;ob=ob+1) begin: bank
      wire hit;
      wire [7:0] port_data;
      assign hit = registered_valid[ox] && (registered_bank[ox] == ob);
      assign port_data = use_second[ox] ? bank_data1[ob] : bank_data0[ob];
      assign masked[ob] = {8{hit}} & port_data;
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
        staged_valid[q] <= registered_issue_valid[q];
        // Capture data only for admitted waves; old values are ignored
        // when staged_valid is low.
        if (registered_issue_valid[q]) begin
          staged_wave_id[q] <= registered_wave[q];
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
