// V142 synthesizable registered Wave32 producer multicast capture.
// Single 32*LANES-bit writeback vector may fill 1, 2, or 3 matching
// source slots in the SAME cycle; not an FMA or complete operand collector.
// clear starts a new instruction; no RF response path in this block.
module vektor_wave32_broadcast_capture #(
  parameter integer LANES=32,
  parameter integer REG_BITS=6
)(
  input wire clk, input wire rst_n, input wire clear,
  input wire [3*REG_BITS-1:0] src_regs,
  input wire wb_valid,
  input wire [REG_BITS-1:0] wb_reg,
  input wire [LANES*32-1:0] wb_value,
  output reg [2:0] captured_valid,
  output reg [3*LANES*32-1:0] captured_data
);
  localparam integer WIDTH=LANES*32;
  integer i;
  always @(posedge clk) begin
    if (!rst_n || clear) begin
      captured_valid <= 3'b000;
      captured_data <= {3*WIDTH{1'b0}};
    end else if (wb_valid) begin
      for (i=0;i<3;i=i+1) begin
        if (!captured_valid[i] && src_regs[i*REG_BITS +: REG_BITS]==wb_reg) begin
          captured_valid[i] <= 1'b1;
          captured_data[i*WIDTH +: WIDTH] <= wb_value;
        end
      end
    end
  end
endmodule
