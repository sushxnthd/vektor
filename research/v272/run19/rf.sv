// V272 run19: isolated double-pumped 1R/1W RF vs matched 2R/1W RF.
// Architectural experiment ONLY. No SRAM inference, clock-tree or STA claim.
module v272_pumped_rf #(parameter ADDRW=4, DATAW=32)(
  input wire clk2x, phase, rst,
  input wire rd_en0, rd_en1,
  input wire [ADDRW-1:0] rd_addr0, rd_addr1,
  input wire wr_en,
  input wire [ADDRW-1:0] wr_addr,
  input wire [DATAW-1:0] wr_data,
  output reg rd_valid0, rd_valid1,
  output reg [DATAW-1:0] rd_data0, rd_data1
);
  reg [DATAW-1:0] bank [0:(1<<ADDRW)-1];
  always @(posedge clk2x) begin
    if (rst) begin rd_valid0 <= 0; rd_valid1 <= 0; end
    else if (!phase) begin
      if (wr_en) bank[wr_addr] <= wr_data;
      rd_valid0 <= rd_en0; rd_valid1 <= 0;
      if (rd_en0)
        rd_data0 <= (wr_en && wr_addr == rd_addr0) ? wr_data : bank[rd_addr0];
    end else begin
      rd_valid1 <= rd_en1;
      if (rd_en1) rd_data1 <= bank[rd_addr1];
    end
  end
endmodule

module v272_two_read_rf #(parameter ADDRW=4, DATAW=32)(
  input wire clk, rst,
  input wire rd_en0, rd_en1,
  input wire [ADDRW-1:0] rd_addr0, rd_addr1,
  input wire wr_en,
  input wire [ADDRW-1:0] wr_addr,
  input wire [DATAW-1:0] wr_data,
  output reg rd_valid0, rd_valid1,
  output reg [DATAW-1:0] rd_data0, rd_data1
);
  reg [DATAW-1:0] bank [0:(1<<ADDRW)-1];
  always @(posedge clk) begin
    if (rst) begin rd_valid0 <= 0; rd_valid1 <= 0; end
    else begin
      if (wr_en) bank[wr_addr] <= wr_data;
      rd_valid0 <= rd_en0; rd_valid1 <= rd_en1;
      if (rd_en0)
        rd_data0 <= (wr_en && wr_addr == rd_addr0) ? wr_data : bank[rd_addr0];
      if (rd_en1)
        rd_data1 <= (wr_en && wr_addr == rd_addr1) ? wr_data : bank[rd_addr1];
    end
  end
endmodule

module v272_one_read_rf #(parameter ADDRW=4, DATAW=32)(
  input wire clk, rst, rd_en, wr_en,
  input wire [ADDRW-1:0] rd_addr, wr_addr,
  input wire [DATAW-1:0] wr_data,
  output reg rd_valid,
  output reg [DATAW-1:0] rd_data
);
  reg [DATAW-1:0] bank [0:(1<<ADDRW)-1];
  always @(posedge clk) begin
    if (rst) rd_valid <= 0;
    else begin
      if (wr_en) bank[wr_addr] <= wr_data;
      rd_valid <= rd_en;
      if (rd_en) rd_data <= (wr_en && wr_addr == rd_addr) ? wr_data : bank[rd_addr];
    end
  end
endmodule
