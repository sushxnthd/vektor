// V293 experimental operand bypass. No SRAM, floorplan, or energy claim.
// Two implementations share the same 4x32b capacity and single RF-read interface.
// LOCAL=1: four direct-mapped bank-local entries. LOCAL=0: four-entry fully
// associative, round-robin global control. Stronger banked control is identical
// to LOCAL=1 and is a decisive novelty/equal-budget comparator.
module v293_bypass #(
  parameter LOCAL = 1
)(
  input wire clk, rst,
  input wire req_valid,
  input wire [7:0] req_addr,
  input wire [31:0] rf_data,
  input wire wr_en,
  input wire [7:0] wr_addr,
  input wire [31:0] wr_data,
  output wire out_valid,
  output wire [31:0] out_data,
  output wire rf_read,
  output wire hit
);
  wire write_forward = wr_en && (wr_addr == req_addr);
  wire [31:0] hit_data;
  assign out_valid = req_valid;
  assign out_data = write_forward ? wr_data : (hit ? hit_data : rf_data);
  assign rf_read = req_valid && !hit && !write_forward;

  generate if (LOCAL) begin : banked
    reg [3:0] valid;
    reg [7:0] tag [0:3];
    reg [31:0] value [0:3];
    wire [1:0] bank = req_addr[1:0];
    integer i;
    assign hit = valid[bank] && tag[bank] == req_addr;
    assign hit_data = value[bank];
    always @(posedge clk) begin
      if (rst) begin
        valid <= 4'b0000;
      end else begin
        if (req_valid && !hit && !write_forward) begin
          valid[bank] <= 1'b1;
          tag[bank] <= req_addr;
          value[bank] <= rf_data;
        end
        if (wr_en) begin
          for (i=0;i<4;i=i+1)
            if (valid[i] && tag[i] == wr_addr) valid[i] <= 1'b0;
        end
      end
    end
  end else begin : global_cache
    reg [3:0] valid;
    reg [7:0] tag [0:3];
    reg [31:0] value [0:3];
    reg [1:0] victim;
    reg found;
    reg [31:0] found_value;
    integer i;
    integer j;
    always @* begin
      found = 1'b0;
      found_value = 32'b0;
      for (i=0;i<4;i=i+1) begin
        if (!found && valid[i] && tag[i] == req_addr) begin
          found = 1'b1;
          found_value = value[i];
        end
      end
    end
    assign hit = found;
    assign hit_data = found_value;
    always @(posedge clk) begin
      if (rst) begin
        valid <= 4'b0000;
        victim <= 2'b00;
      end else begin
        if (req_valid && !hit && !write_forward) begin
          valid[victim] <= 1'b1;
          tag[victim] <= req_addr;
          value[victim] <= rf_data;
          victim <= victim + 2'd1;
        end
        if (wr_en) begin
          for (j=0;j<4;j=j+1)
            if (valid[j] && tag[j] == wr_addr) valid[j] <= 1'b0;
        end
      end
    end
  end endgenerate
endmodule
