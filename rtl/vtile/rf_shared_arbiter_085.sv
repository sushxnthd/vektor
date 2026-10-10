// Experimental fixed-priority shared RF bank arbiter (Vektor-085).
// Synthesizable candidate only: NOT RTL-simulated or timing-verified.
module rf_shared_arbiter_085 #(
  parameter integer BANKS=4,
  parameter integer BANK_W=2,
  parameter integer READ_REQS=8,
  parameter integer WRITE_REQS=4,
  parameter integer PORTS_PER_BANK=3,
  parameter integer WB_PORTS_PER_BANK=1,
  parameter integer READ_CAP_PER_BANK=3
)(
  input wire [READ_REQS-1:0] rd_valid,
  input wire [READ_REQS*BANK_W-1:0] rd_bank,
  input wire [WRITE_REQS-1:0] wr_valid,
  input wire [WRITE_REQS*BANK_W-1:0] wr_bank,
  output reg [READ_REQS-1:0] rd_grant,
  output reg [WRITE_REQS-1:0] wr_grant
);
  integer used [0:BANKS-1];
  integer wused [0:BANKS-1];
  integer rused [0:BANKS-1];
  integer b,i;
  always @* begin
    rd_grant='0; wr_grant='0;
    for(b=0;b<BANKS;b=b+1) begin
      used[b]=0; wused[b]=0; rused[b]=0;
    end
    for(i=0;i<WRITE_REQS;i=i+1) begin
      if(wr_valid[i] && wr_bank[i*BANK_W+:BANK_W]<BANKS) begin
        if(used[wr_bank[i*BANK_W+:BANK_W]]<PORTS_PER_BANK &&
           wused[wr_bank[i*BANK_W+:BANK_W]]<WB_PORTS_PER_BANK) begin
          wr_grant[i]=1'b1;
          used[wr_bank[i*BANK_W+:BANK_W]]=used[wr_bank[i*BANK_W+:BANK_W]]+1;
          wused[wr_bank[i*BANK_W+:BANK_W]]=wused[wr_bank[i*BANK_W+:BANK_W]]+1;
        end
      end
    end
    for(i=0;i<READ_REQS;i=i+1) begin
      if(rd_valid[i] && rd_bank[i*BANK_W+:BANK_W]<BANKS) begin
        if(used[rd_bank[i*BANK_W+:BANK_W]]<PORTS_PER_BANK &&
           rused[rd_bank[i*BANK_W+:BANK_W]]<READ_CAP_PER_BANK) begin
          rd_grant[i]=1'b1;
          used[rd_bank[i*BANK_W+:BANK_W]]=used[rd_bank[i*BANK_W+:BANK_W]]+1;
          rused[rd_bank[i*BANK_W+:BANK_W]]=rused[rd_bank[i*BANK_W+:BANK_W]]+1;
        end
      end
    end
  end
endmodule
