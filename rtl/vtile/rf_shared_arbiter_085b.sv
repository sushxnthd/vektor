// Vektor-085b bank-major fixed-priority RF grants, static bank loops.
module rf_shared_arbiter_085b #(
  parameter integer BANKS=4, BANK_W=2, READ_REQS=8, WRITE_REQS=4,
  PORTS_PER_BANK=3, WB_PORTS_PER_BANK=1, READ_CAP_PER_BANK=3
)(
  input wire [READ_REQS-1:0] rd_valid,
  input wire [READ_REQS*BANK_W-1:0] rd_bank,
  input wire [WRITE_REQS-1:0] wr_valid,
  input wire [WRITE_REQS*BANK_W-1:0] wr_bank,
  output reg [READ_REQS-1:0] rd_grant,
  output reg [WRITE_REQS-1:0] wr_grant
);
  integer b,i,used,wused,rused;
  always @* begin
    rd_grant='0;wr_grant='0;
    for(b=0;b<BANKS;b=b+1) begin
      used=0;wused=0;rused=0;
      for(i=0;i<WRITE_REQS;i=i+1) begin
        if(wr_valid[i] && wr_bank[i*BANK_W+:BANK_W]==b &&
           used<PORTS_PER_BANK && wused<WB_PORTS_PER_BANK) begin
          wr_grant[i]=1'b1;
          used=used+1;wused=wused+1;
        end
      end
      for(i=0;i<READ_REQS;i=i+1) begin
        if(rd_valid[i] && rd_bank[i*BANK_W+:BANK_W]==b &&
           used<PORTS_PER_BANK && rused<READ_CAP_PER_BANK) begin
          rd_grant[i]=1'b1;
          used=used+1;rused=rused+1;
        end
      end
    end
  end
endmodule
